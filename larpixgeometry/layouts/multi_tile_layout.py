"""
This script produces a YAML file containing one variable and three dictionaries,
describing the physical structures (e.g. pixel pads and anode tiles) and
software/electrical associations (e.g. IO group, IO channel, chip ID) for
a multi-tile LArPix anode

- tile_layout_version: version of the LArPix single-tile layout
- multitile_layout_version: version of the multi-tile layout in the X.Y.Z. format
    where X represents the ASIC version, Y represents the single-tile version
    (incremented from 0), and Z represents the number of tiles in the layout.
- pixel_pitch: pixel pitch value in mm
- tile_positions: dictionary where the key is tile ID of type integer
    and the value is a pair of vectors: position and orientation
    of the tile
- tile_chip_to_io: nested dictionary where the first key is tile ID
    and the second key is chip ID and the value is IO channel +
    1000 * IO group. Tile ID, chip ID, IO channel, and IO group are
    all type integers
- chip_channel_to_position: dictionary where the key is channel ID +
    1000 * chip ID and the value is (x-position, y-position),
    stored as multiples of the pixel pitch of type integer
"""

import yaml

import larpixgeometry.pixelplane

LAYOUT_VERSION = '2.4.0'
FORMAT_VERSION = '2.0.16'

PIXEL_FILE = 'layout-%s.yaml' % LAYOUT_VERSION
PIXEL_PITCH = 4.434

N_TILES = 16
N_IO_CHANNELS = 4

with open(PIXEL_FILE, 'r') as pf:
    board = larpixgeometry.pixelplane.PixelPlane.fromDict(yaml.load(pf, Loader=yaml.FullLoader))

chipids = list(board.chips.keys())

tiles = list(range(1,N_TILES+1))
io_channels = [[] for i in range(N_IO_CHANNELS)]

## These numbers were taken from a standard network configuration
## for a LArPix tile
io_channels[0] = list(range(11,35))
io_channels[1] = list(range(35,61))
io_channels[2] = list(range(61,91))
io_channels[3] = list(range(91,111))

## These positions comes from the GDML file.
## The numbers are in mm and were provided by Patrick Koller.
## The anode is on the yz plane with the pixels oriented
## towards the positive x axis
tile_positions = {1: [[0,465.2,-155.2],[1,0,0]],
                  2: [[0,465.2,155.2],[1,0,0]],
                  3: [[0,155.2,-155.2],[1,0,0]],
                  4: [[0,155.2,155.2],[1,0,0]],
                  5: [[0,-155.2,-155.2],[1,0,0]],
                  6: [[0,-155.2,155.2],[1,0,0]],
                  7: [[0,-465.2,-155.2],[1,0,0]],
                  8: [[0,-465.2,155.2],[1,0,0]],
                  9: [[0,465.2,-155.2],[-1,0,0]],
                  10: [[0,465.2,155.2],[-1,0,0]],
                  11: [[0,155.2,-155.2],[-1,0,0]],
                  12: [[0,155.2,155.2],[-1,0,0]],
                  13: [[0,-155.2,-155.2],[-1,0,0]],
                  14: [[0,-155.2,155.2],[-1,0,0]],
                  15: [[0,-465.2,-155.2],[-1,0,0]],
                  16: [[0,-465.2,155.2],[-1,0,0]]}

tile_chip_io_channel_io_group = {it:{} for it in range(1,N_TILES+1)}

tile_io_group_io_channel = {t: [t*1000+i for i in range(1,N_IO_CHANNELS+1)] for t in tiles}

for tile_id in tile_io_group_io_channel:
    for i,io in enumerate(io_channels):
        for chip in io:
            tile_chip_io_channel_io_group[tile_id][chip] = tile_io_group_io_channel[tile_id][i]

chip_channel = {}

for chip in chipids:
    for channel, pixel in enumerate(board.chips[chip].channel_connections):
        if pixel.x !=0 and pixel.y != 0:
            key = chip*1000 + channel
            chip_channel[key] = [round(pixel.x / PIXEL_PITCH), round(pixel.y / PIXEL_PITCH)]

if __name__ == "__main__":
    with open('multi_tile_layout-%s.yaml' % FORMAT_VERSION, 'w') as f:
        yaml.dump({'tile_layout_version': LAYOUT_VERSION,
                   'multitile_layout_version': FORMAT_VERSION,
                   'pixel_pitch': PIXEL_PITCH,
                   'tile_positions': tile_positions,
                   'tile_chip_to_io': tile_chip_io_channel_io_group,
                   'chip_channel_to_position': chip_channel}, f)
