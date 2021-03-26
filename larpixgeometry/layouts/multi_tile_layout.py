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
    and the value is the position vector of the tile center
- tile_orientations: dictionary where the key is tile ID of type integer
    and the value is the direction vector of the tile, with respect to
    the reference frame in larpix-geometry
- tile_chip_to_io: nested dictionary where the first key is tile ID
    and the second key is chip ID and the value is (IO channel, IO group).
    Tile ID, chip ID, IO channel, and IO group are all type integers
- chip_channel_to_position: dictionary where the key is (channel ID, chip ID)
    and the value is (x-position, y-position), stored as multiples of the pixel pitch
    of type integer
- tile_indeces: dictionary where the key is the tile ID and the value is a tuple in
    the format (module ID, anode ID, tile ID within the anode)
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
    Function that generates the multi-layout YAML file.

    Args:
        tile_layout_file (str): YAML file containing the tile layout
        network_config_file (str): JSON file containing the network configuration
            or txt file with a list of JSON files (one per tile)
        n_tiles (int): number of tiles
        pixel_pitch (float): value of pixel pitch, default is PIXEL_PITCH
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
    tile_indeces = {1:  [1,1,1],
                    2:  [1,1,2],
                    3:  [1,1,3],
                    4:  [1,1,4],
                    5:  [1,1,5],
                    6:  [1,1,6],
                    7:  [1,1,7],
                    8:  [1,1,8],
                    9:  [1,2,1],
                    10: [1,2,2],
                    11: [1,2,3],
                    12: [1,2,4],
                    13: [1,2,5],
                    14: [1,2,6],
                    15: [1,2,7],
                    16: [1,2,8]}

    tile_positions = {1:  [-315.1745, 465.2,-155.2],
                      2:  [-315.1745, 465.2, 155.2],
                      3:  [-315.1745, 155.2,-155.2],
                      4:  [-315.1745, 155.2, 155.2],
                      5:  [-315.1745,-155.2,-155.2],
                      6:  [-315.1745,-155.2, 155.2],
                      7:  [-315.1745,-465.2,-155.2],
                      8:  [-315.1745,-465.2, 155.2],
                      9:  [ 315.1745, 465.2,-155.2],
                      10: [ 315.1745, 465.2, 155.2],
                      11: [ 315.1745, 155.2,-155.2],
                      12: [ 315.1745, 155.2, 155.2],
                      13: [ 315.1745,-155.2,-155.2],
                      14: [ 315.1745,-155.2, 155.2],
                      15: [ 315.1745,-465.2,-155.2],
                      16: [ 315.1745,-465.2, 155.2]}

    tpc_centers = {1: [0, -218.236, 0],
                   2: [0, -218.236, 0]}

                             # z  y  x
    tile_orientations = {1:  [ 1,-1, 1],
                         2:  [ 1, 1,-1],
                         3:  [ 1,-1, 1],
                         4:  [ 1, 1,-1],
                         5:  [ 1,-1, 1],
                         6:  [ 1, 1,-1],
                         7:  [ 1,-1, 1],
                         8:  [ 1, 1,-1],
                         9:  [-1,-1, 1],
                         10: [-1, 1,-1],
                         11: [-1,-1, 1],
                         12: [-1, 1,-1],
                         13: [-1,-1, 1],
                         14: [-1, 1,-1],
                         15: [-1,-1, 1],
                         16: [-1, 1,-1]}

    tile_chip_io_channel_io_group = {it:{} for it in range(1,n_tiles+1)}

    for tile_id in io_channels_tile:
        io_channels = io_channels_tile[tile_id]
        for io in io_channels:
            for chip in io_channels[io]:
                tile_chip_io_channel_io_group[tile_id][chip] = tile_id*1000 + io

    chip_channel = {}

    xs = []
    ys = []
    for chip in chipids:
        for channel, pixel in enumerate(board.chips[chip].channel_connections):
            if pixel.x !=0 and pixel.y != 0:
                xs.append(pixel.x)
                ys.append(pixel.y)

    for chip in chipids:
        for channel, pixel in enumerate(board.chips[chip].channel_connections):
            if pixel.x !=0 and pixel.y != 0:
                key = chip*1000+channel
                chip_channel[key] = [round((pixel.x - min(xs))/pixel_pitch),
                                     round((pixel.y - min(ys))/pixel_pitch)]

    with open('multi_tile_layout-%s.yaml' % FORMAT_VERSION, 'w') as f:
        yaml.dump({'tile_layout_version': LAYOUT_VERSION,
                   'multitile_layout_version': FORMAT_VERSION,
                   'pixel_pitch': pixel_pitch,
                   'tile_positions': tile_positions,
                   'tile_orientations': tile_orientations,
                   'tpc_centers': tpc_centers,
                   'tile_chip_to_io': tile_chip_io_channel_io_group,
                   'tile_indeces': tile_indeces,
                   'chip_channel_to_position': chip_channel}, f)

if __name__ == "__main__":
    fire.Fire(generate_layout)
