#!/bin/sh

# generate the display as svg image
python /mnt/us/extensions/kindle-display/generate_svg.py /tmp/display.svg

# convert the svg image to png
LD_LIBRARY_PATH=/mnt/us/extensions/rsvg-convert/lib:/usr/lib:/lib /mnt/us/extensions/rsvg-convert/bin/rsvg-convert /tmp/display.svg > /tmp/display.png

# crush the png, make it grayscale
/mnt/us/extensions/pngcrush -c 0 -q /tmp/display.png /tmp/display_final.png

# clearing to avoid artifacts
# this makes the update "flicker" and I did not see any artifacts that annoy me more than that yet
# eips -c
# display the new image
eips -g /tmp/display_final.png
