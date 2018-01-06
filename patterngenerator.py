'''
Generate pixel plane patterns.

'''

from itertools import product
import numpy as np

def pixels_plain_grid(nx, ny, dx, dy):
    '''
    A plain grid of no-pad no-focus pixels.

    '''
    pixels = []
    for i, (x_index, y_index) in enumerate(product(range(nx),
            range(ny))):
        x = x_index * dx
        y = y_index * dy
        pixel = (i, x, y, [], [])
        pixels.append(pixel)
    return pixels

def pixels_triangle_grid(repetition_period, nblocksx, nblocksy, startx,
        starty, start_index):
    '''
    A grid of triangle pixels specific to the LArPix sensor board.

    '''
    pixels = []
    unit = repetition_period / 8.0
    subgrid = np.array(  # Laid out here in the orientation on the board
              [[2*unit, unit],                [6*unit, unit],
        [unit, 2*unit], [3*unit, 2*unit], [5*unit, 2*unit], [7*unit, 2*unit],
               [2*unit, 10/3.*unit],          [6*unit, 10/3.*unit],
               [2*unit, 14/3.*unit],          [6*unit, 14/3.*unit],
        [unit, 6*unit], [3*unit, 6*unit], [5*unit, 2*unit], [7*unit, 2*unit],
               [2*unit, 7*unit],              [6*unit, 7*unit]])
    pixels_per_grid = len(subgrid)
    for block_index, (xblock, yblock) in enumerate(product(
            range(nblocksx), range(nblocksy))):
        pixelids = range(block_index*pixels_per_grid + start_index,
                (block_index+1)*pixels_per_grid + start_index)
        offset = np.array([xblock*repetition_period + startx,
            yblock*repetition_period + starty])
        pixel_locations = subgrid + offset
        for pixelid, (x, y) in zip(pixelids, pixel_locations):
            pixels.append((pixelid, x, y, [], []))
    return pixels



grid_4x4_assignments = [1, 2, 0, 3, 5, 6, 4, 7, 8, 11, 9, 10, 12, 15, 13, 14]
'''
Index in flattened ``pixelids`` list (from the chip side)::

0  1  2  3
4  5  6  7
8  9  10 11
12 13 14 15

Channel assignments (right side up) (from the chip side)::

2  0  1  3      18 16 17 19
6  4  5  7  or  22 20 21 23
8  10 11 9      24 26 27 25
12 14 15 13     28 30 31 29

'''

triangle_assignments = [0, 1, 3, 4, 2, 5, 6, 7, 8, 9, 10, 13, 11, 12, 14, 15]
'''
Index in flattened ``pixelids`` list (from the chip side)::

   0           1
2     3     4     5
   6           7
   8           9
10    11    12    13
   14          15

Channel assignments (right-side up) (from the chip side)::

   0           1               16          17
4     2     3     5         20    18    19    21
   6           7       or      22          23
   8           9               24          25
10    12    13    11        26    28    29    27
   14          15              30          31

'''

def assign_pixels(pixelids, assignments, right_side_up=True):
    '''
    Return a list assigning the given pixelids to a chip's channels
    using the provided assignment array.

    The right-side up configuration (``right_side_up=True``) of the chip
    is (viewed from above), channels 0-15 on the left and channels 16-31
    on the right. The upside-down configuration is reversed: channels
    16-31 on the left, and channels 0-15 on the right.

    Since the convention is that channel id is given by position in the
    list, this function always returns assignments to channels 0-15.
    If the given grid should be assigned to channels 16-31, just
    concatenate it with the assignments for 0-15.

    ``assignments[i]`` gives the index in the final list of
    ``pixelids[i]``.

    '''
    if not right_side_up:
        assignments = assignments[::-1]
    channel_connections = []
    for i, pixelid in enumerate(pixelids):
        channel_connections.append(pixelids[assignments[channel_id]])
    return channel_connections
