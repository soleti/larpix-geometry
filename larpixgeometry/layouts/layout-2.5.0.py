'''
Generate a YAML file with the pixel layout and chip connections for a 2x4 array
(x,y) of packaged 10x10 pixel tiles

Uses same layout as layout-2.4.0.py for each tile

'''
import yaml
import patterngenerator as pg

filename = 'layout-2.5.0.yaml'
format_version = '1.0.0' # use chip keys

pixels = []
pixelids = dict()
chips = []

N_TILES_X = 2 # number of tiles in X dim
N_TILES_Y = 4 # number of tiles in Y dim
N_IO_CHANNELS_TILE = 4 # number of io channels on each tile
N_CHIPS_IO_CHANNEL = 25 # number of chips per io channel
PIXEL_PITCH = 4.434 # mm
TILE_WIDTH = PIXEL_PITCH*70 # mm
TILE_HEIGHT = PIXEL_PITCH*70 # mm

tile_array = [(i,j) for i in range(N_TILES_X) for j in range(N_TILES_Y)]

# all tiles have same io_group
io_group = 1
# lookup table for io_channels on each tile
io_channels = dict([(tile,
    list(range(i+1,i+N_IO_CHANNELS_TILE+1)))
    for i,tile in enumerate(tile_array)
    ])
# lookup table for chip_ids on each io_channel
chip_ids = dict([(tile,
    dict([(io_channel,
        list(range(11+j*N_CHIPS_IO_CHANNEL, 11+(j+1)*N_CHIPS_IO_CHANNEL)))
        for j,io_channel in enumerate(io_channels[tile])
        ]))
    for tile in tile_array
    ])

two_digit_xy = lambda x: ((x%10-1), 9-(x//10-1))
last_column_xy = lambda x: (9, 9-(x//10-2))
last_row_xy = lambda x: ((x%100-1), 0)

for tile in tile_array:
    tile_x_i, tile_y_i = tile
    tile_x = (tile_x_i - (N_TILES_X-1)/2) * TILE_WIDTH
    tile_y = (tile_y_i - (N_TILES_Y-1)/2) * TILE_HEIGHT

    for io_channel in io_channels[tile]:
        for chip in chip_ids[tile][io_channel]:
            if chip < 100:
                x,y = two_digit_xy(chip)
            elif chip>=100:
                x,y = last_row_xy(chip)

            if chip%10==0:
                x,y = last_column_xy(chip)

            x = x * 7 * PIXEL_PITCH + PIXEL_PITCH/2 - TILE_WIDTH/2 + tile_x
            y = y * 7 * PIXEL_PITCH + PIXEL_PITCH/2 - TILE_HEIGHT/2 + tile_y
            pixels.extend(pg.pixels_plain_grid(PIXEL_PITCH, 1, 1, x, y, len(pixels), batch_size=7, pixels_per_grid=49))

        for chip_idx, chip in enumerate(chip_ids[tile][io_channel]):
            chip_idx = len(pixelids)
            chip_key = '{}-{}-{}'.format(io_group, io_channel, chip)
            # Bool value is argument to right_side_up
            chip_pixels = list(range(chip_idx*49, chip_idx*49 + 49))
            pixelids[chip_key] = (True, 'plain', chip_pixels)

for chip_key, (right_side_up, shape, ids) in pixelids.items():
    assignment = pg.grid_7x7_assignments_0_64_v2_2_1
    channels = pg.assign_pixels(ids, assignment, right_side_up, range(64))
    chips.append([chip_key, channels])
print('chips',len(chips))
print('pixels',len(pixels))

with open(filename, 'w') as f:
    yaml.dump({'format_version': format_version, 'pixels': pixels, 'chips': chips, 'x': -(TILE_WIDTH * N_TILES_X)/2, 'y': -(TILE_HEIGHT * N_TILES_Y)/2,
        'width': TILE_WIDTH * N_TILES_X, 'height': TILE_HEIGHT * N_TILES_Y}, f)
