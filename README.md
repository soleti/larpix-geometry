larpix-geometry
===============

Handle pixel and TPC geometry for LArPix

Overview
---------

Pixel geometry and channel assignments are stored in YAML configuration
files. pixelplane.py will read a configuration file and allow easy
access to channel-to-(x,y) conversion and other convenient
relationships.

patterngenerator.py contains code for generating arbitrary
configurations of pixel planes. Individual python scripts are needed per
pixel/chip geometry.

draw_plane.py reads in a YAML configuration file and draws the pixel
plane and channel connections in a PDF file for easy visual inspection
and reference.

Usage
---------

The scripts can be executed with no arguments.

Here is how to use the pixelplane module.

```python
from pixelplane import *
import yaml

with open('pixel_geometry.yaml', 'r') as f:
    board = PixelPlane.fromDict(yaml.load(f))

chip_keys = list(board.chips.keys())
chip0 = board.chips[chip_keys[0]]
print('Retrieving {}'.format(chip0.chip_key))
# print list of (x, y) for each channel
print('Channel ID |     Position\n-----------|-------------')
for channel, pixel in enumerate(chip0.channel_connections):
    print('  %02d       | (%.1f, %.1f)' % (channel, pixel.x, pixel.y))

# Find which channel corresponds to pixel 100
pixel100 = board.pixels[100]
chip, channel = pixel100.channel_connection
print('Pixel 100 is connected to chip {}, channel {}'.format(chip.chip_key,
  channel))

# Find which channels correspond to pixels with x locations greater than 100
connection_list = board.channels_where(lambda pixel:pixel.x > 100)
for chip, channel in connection_list:
    print('Chip {}, channel {}'.format(chip.chip_key, channel))
```

Units and coordinates
---------------------

All units in ``layout-*.py`` scripts and output YAML files are
millimeters unless otherwise explicitly specified. In ``draw_plane.py``,
the units are 1/72 of an inch, which is the base unit used by the PDF
generator tool ``reportlab``, and all other quantities are converted
into the base units using the ``inch`` and ``cm`` conversion factors
provided by ``reportlab``.

The coordinate origin in the layout files is in the top left. X
increases to the right as usual, and Y increases down the page, as
is the convention for web layout. (Unfortunately, the ``reportlab``
tool uses the math/physics convention of Y starting at the bottom and
increasing up the page, so the coordinates are explicitly transformed in
``draw_plane.py``.)

YAML layout files
-----------------

The YAML layout files specify both the pixel geometry and the connection
map between pixels and ASIC channels. The meaning of each field is as
follows:

- ``chips``: A nested list containing one element per ASIC. Each element is
  structured as a 2-element list, with the 0th element being the Chip
key, and the 1st element being a list where the ``i``-th element is the Pixel
ID connected to Channel ``i``. (A value of ``null`` means the
channel is not connected/bonded to any pixel.) For example:

```
chips:
- - '1-1-1'  # <-- Chip key = 1-1-1
  - - 14  # <-- Channel 0 connected to Pixel 14
    - 13  # <-- Channel 1 connected to Pixel 13
...
- - '1-2-20'  # <-- Chip key = 1-2-20
  - - 821 # <-- Chip 20, Channel 0 connected to Pixel 821
    - 822 # <-- Chip 20, Channel 1 connected to Pixel 822
    - null # <-- Chip 20, Channel 2 not bonded to a pixel
...
```

- ``pixels``: A nested list containing one element per pixel. Each
  element is a 5-element list with the following structure:
  1. Pixel ID
  2. x position
  3. y position
  4. list of vertices of collection pad (may be empty)
  5. list of vertices of focusing grid (may be empty)

- ``x``, ``y``: the x and y positions of the top-left corner of the
  bounding rectangle of the pixel plane (plus a small margin). Used for
  determining scaling and placement when drawing the pixel grid.

- ``width``, ``height``: the width and height of the bounding rectangle
  of the pixel plane. Used for determining scaling and placement when
  drawing the pixel grid.

