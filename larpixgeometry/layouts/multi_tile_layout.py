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

import json
import fire
import yaml
import larpixgeometry.pixelplane

LAYOUT_VERSION = '2.4.0'
FORMAT_VERSION = '2.0.16'
PIXEL_PITCH = 4.434

def generate_layout(tile_layout_file, network_config_file, n_tiles, pixel_pitch=PIXEL_PITCH):
    """
    Function that generates the multi-layout YAML file
    """

    with open(tile_layout_file, 'r') as pf:
        board = larpixgeometry.pixelplane.PixelPlane.fromDict(yaml.load(pf, Loader=yaml.FullLoader))

    with open(network_config_file, 'r') as nc:
        if '.txt' in network_config_file:
            network_configs = nc.readlines()
        elif '.json' in network_config_file:
            network_configs = [network_config_file]*n_tiles
        else:
            raise ValueError("Network configuration file must have txt or json extension")

    chipids = list(board.chips.keys())

    io_channels_tile = {}

    for it,network_config in enumerate(network_configs):

        with open(network_config, 'r') as nc:
            nc_json = json.load(nc)

        io_channels = nc_json['network']['1']
        io_channels_tile[it+1] = {}

        for io_channel in io_channels:
            nodes = io_channels[io_channel]['nodes']
            for node in nodes:
                chip_id = node['chip_id']
                if isinstance(chip_id, int):
                    if int(io_channel) in io_channels_tile[it+1]:
                        io_channels_tile[it+1][int(io_channel)].append(chip_id)
                    else:
                        io_channels_tile[it+1][int(io_channel)] = [chip_id]

    ## These positions comes from the GDML file.
    ## The numbers are in mm and were provided by Patrick Koller.
    ## The anode is on the yz plane with the pixels oriented
    ## towards the positive x axis
    tile_positions = {1: [[-315.1745,465.2,-155.2],[1,0,0]],
                      2: [[-315.1745,465.2,155.2],[1,0,0]],
                      3: [[-315.1745,155.2,-155.2],[1,0,0]],
                      4: [[-315.1745,155.2,155.2],[1,0,0]],
                      5: [[-315.1745,-155.2,-155.2],[1,0,0]],
                      6: [[-315.1745,-155.2,155.2],[1,0,0]],
                      7: [[-315.1745,-465.2,-155.2],[1,0,0]],
                      8: [[-315.1745,-465.2,155.2],[1,0,0]],
                      9: [[-315.1745,465.2,-155.2],[-1,0,0]],
                      10: [[315.1745,465.2,155.2],[-1,0,0]],
                      11: [[315.1745,155.2,-155.2],[-1,0,0]],
                      12: [[315.1745,155.2,155.2],[-1,0,0]],
                      13: [[315.1745,-155.2,-155.2],[-1,0,0]],
                      14: [[315.1745,-155.2,155.2],[-1,0,0]],
                      15: [[315.1745,-465.2,-155.2],[-1,0,0]],
                      16: [[315.1745,-465.2,155.2],[-1,0,0]]}

    tile_chip_io_channel_io_group = {it:{} for it in range(1,n_tiles+1)}

    for tile_id in io_channels_tile:
        io_channels = io_channels_tile[tile_id]
        for io in io_channels:
            for chip in io_channels[io]:
                tile_chip_io_channel_io_group[tile_id][chip] = tile_id*1000+io

    chip_channel = {}

    for chip in chipids:
        for channel, pixel in enumerate(board.chips[chip].channel_connections):
            if pixel.x !=0 and pixel.y != 0:
                key = chip*1000 + channel
                chip_channel[key] = [round(pixel.x / pixel_pitch), round(pixel.y / pixel_pitch)]

    with open('multi_tile_layout-%s2.yaml' % FORMAT_VERSION, 'w') as f:
        yaml.dump({'tile_layout_version': LAYOUT_VERSION,
                   'multitile_layout_version': FORMAT_VERSION,
                   'pixel_pitch': pixel_pitch,
                   'tile_positions': tile_positions,
                   'tile_chip_to_io': tile_chip_io_channel_io_group,
                   'chip_channel_to_position': chip_channel}, f)

if __name__ == "__main__":
    fire.Fire(generate_layout)
