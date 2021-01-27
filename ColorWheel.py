
# chooses an infinite* series of unique colors by rotating 10pi degrees around the color wheel
# uses the static variable currentHue so that a different color is chosen each time
# getNextHue is called.

from math import pi

# update the current hue and return it
# currentHue is represented in degrees from [0, 360)
def getNextHue():
    # initialize currentHue to 0 on first call
    if "currentHue" not in getNextHue.__dict__: 
        getNextHue.currentHue = 0
    else:
        getNextHue.currentHue = (getNextHue.currentHue + 10*pi) % 360
    
    return getNextHue.currentHue

# get a *unique hue for each integer index
def getHueByIndex(index):
    return (index*10*pi) % 360
