#
#  API Reference:
#   https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc
#

from pydbus import SystemBus
from xml.etree import ElementTree as ET
import time, sys

_max_search_time = 40


def forget_all():
    bus = SystemBus() # type: pydbus.bus.Bus
    adapter = bus.get('org.bluez', '/org/bluez/hci0')
    _forget_all_devices(bus, adapter)

def force_connect():
    bus = SystemBus() # type: pydbus.bus.Bus
    adapter = bus.get('org.bluez', '/org/bluez/hci0')
    _connect_all_xbox_controllers(bus, adapter)

def pair_new():
    bus = SystemBus() # type: pydbus.bus.Bus
    adapter = bus.get('org.bluez', '/org/bluez/hci0')
    controllers = _find_xbox_controllers(bus, adapter)
    return _pair_xbox_controllers(bus, controllers)

def _find_xbox_controllers(bus, adapter):
    print('looking for controllers')
    start = time.time()
    try:
        adapter.StartDiscovery()
        print('discovery began')
        while time.time() - start < _max_search_time:
            unpaired_devices = _list_xbox_controllers(bus, adapter, paired=False)
            if len(unpaired_devices) > 0:
                print('found {0} controllers'.format(len(unpaired_devices)))
                return unpaired_devices
            time.sleep(5)
    finally:
        print('discovery finished')
        adapter.StopDiscovery()
    return []

def _list_xbox_controllers(bus, adapter, paired=None, connected=None):
    def matches(device):
        if paired is not None:
            if device['paired'] != paired: return False
        if connected is not None:
            if device['connected'] != connected: return False
        return device['name'] == 'Xbox Wireless Controller'
    return [device for device in _list_devices(bus, adapter) if matches(device)]

def _list_devices(bus, adapter):
    data = ET.XML(adapter.Introspect())
    dev_uuids = [node.attrib['name'] for node in data.findall('node')]
    ret_val = []
    for dev_id in dev_uuids:
        device = bus.get('org.bluez', '/org/bluez/hci0/{0}'.format(dev_id))
        ret_val.append({
            'name' : device.Alias,
            'address' : device.Address,
            'dev' : dev_id,
            'trusted' : device.Trusted,
            'paired' : device.Paired,
            'connected' : device.Connected
        })
    return ret_val

def _connect_all_xbox_controllers(bus, adapter):
    unconnected_controllers = _list_xbox_controllers(bus, adapter, paired=True, connected=False)
    for controller in unconnected_controllers:
        device = bus.get('org.bluez', '/org/bluez/hci0/{0}'.format(controller['dev']))
        device.Connect()
        print('connected fine')

def _pair_xbox_controllers(bus, controllers):
    pair_count = 0
    for controller in controllers:
        device = bus.get('org.bluez', '/org/bluez/hci0/{0}'.format(controller['dev']))

        print('attempting to pair to {0}'.format(controller))
        retry = 0
        while retry < 2:
            try:
                device.Pair()
                break
            except:
                print ('connect failed : {0}'.format(sys.exc_info()[0]))
                time.sleep(2)
            retry = retry + 1

        if device.Paired:
            print('pair successful')

            device.Trusted = True
            print('trusted now')

            device.Connect()
            print('connected fine')
            pair_count = pair_count + 1
        else:
            adapter = bus.get('org.bluez', '/org/bluez/hci0')
            adapter.RemoveDevice('/org/bluez/hci0/{0}'.format(controller['dev']))
    return pair_count

def _forget_all_devices(bus, adapter):
    controllers = _list_xbox_controllers(bus, adapter, paired=True)
    for controller in controllers:
        adapter.RemoveDevice('/org/bluez/hci0/{0}'.format(controller['dev']))
        print('removed device {0}'.format(controller))
