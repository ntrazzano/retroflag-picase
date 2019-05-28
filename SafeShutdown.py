#!/usr/bin/env python3
from gpiozero import Button, LED
import os, time, xbox_sync
from signal import pause

powerPin = 3
resetPin = 2
ledPin = 14
powerenPin = 4
hold = 1

led = LED(ledPin)
led.on()

power = LED(powerenPin)
power.on()

#functions that handle button events
def when_pressed():
  led.blink(.2,.2)
  os.system("sudo killall emulationstation && sleep 5s && sudo shutdown -h now")

def when_released():
  led.on()


busy = False

def sync_new():
  global busy
  if busy: return

  print ('going to try and sync any unknown devices')
  led.blink(.2,.2)
  try:
    found_count = xbox_sync.pair_new()
    if found_count == 0:
      print ('nothing found')
      led.blink(0.5, 0.5)
      time.sleep(4)
    else:
      led.off()
      time.sleep(2)
      for x in range(found_count):
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(0.2)
  except:
    print ('failed to sync device')
  led.on()

def forget_all_devices():
  global busy

  print ('going to forget all paired devices')
  led.blink(.6,.6)
  busy = True
  xbox_sync.forget_all()
  time.sleep(5)
  led.on()
  busy = False


rebootBtn = Button(resetPin, hold_time=3)
rebootBtn.when_released = sync_new
rebootBtn.when_held = forget_all_devices

btn = Button(powerPin, hold_time=hold)
btn.when_pressed = when_pressed
btn.when_released = when_released

pause()
