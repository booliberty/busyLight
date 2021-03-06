#!/usr/bin/env python3

import subprocess
import re
from lifxlan import LifxLAN

idleDisplaySleepStatus = subprocess.run(["pmset", "-g", "assertions"],stdout=subprocess.PIPE,universal_newlines=True)
desiredBrightness=65535
bulbColor=(64736, 65535, 32767, 3500)

def checkIdleDisplaySleep():
    blockingProcs = list()
    for assertion in idleDisplaySleepStatus.stdout.splitlines():
        if re.search("pid", assertion):
            if re.search("(PreventUserIdleDisplaySleep|NoDisplaySleepAssertion)", assertion):
                if re.search("(caffeinate|Amphetamine)", assertion) is None:
                    blockingProcs.append(assertion)
    return blockingProcs

def checkForAction(blockingProcs):
    if len(blockingProcs) == 0: 
        print("No blocking processes found.")
        print("Display Sleep NOT Currently Prevented.")
        toggleBulb("off")
    elif len(blockingProcs) > 0:
        print(str(len(blockingProcs))+" blocking processes found:")
        print(blockingProcs)
        print("Display Sleep Currently Prevented.")
        toggleBulb("on")
    else:
        print("Something is wrong. PreventIdleDisplaySleep assertions unknown.  Exiting.")
        exit(1)

def getBulbInfo():
    lifx = LifxLAN(1)
    try:
        bulb = lifx.get_lights()[0]
    except:
        print("No bulbs found.  Exiting.")
        exit(1)
    return bulb

def toggleBulb(position):
    print("Attempting to toggle bulb "+position)
    bulb = getBulbInfo()
    power = bulb.get_power()
    if position == "off":
        if power == 0:
            print("Already off.  All set.  Exiting.")
            exit(0)
        else:
            print("Toggling off.")
            bulb.set_power(0)
    elif position == "on":
        if power != desiredBrightness:
            print("Bulb not at desired brightness.  Increasing")
            bulb.set_power(desiredBrightness)
        else:
            print("Desired brightness already set.")
        if bulb.get_color() != bulbColor:
            print("Setting color: "+bulbColor)
            bulb.set_color(bulbColor)
        else:
            print("Desired color already set.")
    else:
        print("Something is wrong.  Position not defined.")
        exit(1)

def main():
    checkForAction(checkIdleDisplaySleep())

main()

exit(0)
