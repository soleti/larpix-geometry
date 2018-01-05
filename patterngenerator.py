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

def chips_8x4(chipids, nx, ny):
    '''
    Assign the chips sequentially to 8x4 grids of pixels.

    Assumes chips are numbered starting at zero, increasing as x
    increases.

    Pixel IDs:

    0  1  2  3  4  5  6  7
    8  9  10 11 12 13 14 15
    16 17 18 19 20 21 22 23
    24 25 26 27 28 29 30 31

    Channel assignments:

    2  0  1  3  18 16 17 19
    6  4  5  7  22 20 21 23
    8  10 11 9  24 26 27 25
    12 14 15 13 28 30 31 29

    '''
    Dx = 8
    Dy = 4
    pixel_ids = np.arange(nx*ny).reshape(ny, nx)
    print(pixel_ids)
    assignments = {
            0: 1,
            1: 2,
            2: 0,
            3: 3,
            4: 9,
            5: 10,
            6: 8,
            7: 11,
            8: 16,
            9: 19,
            10: 17,
            11: 18,
            12: 24,
            13: 27,
            14: 25,
            15: 26,
            16: 5,
            17: 6,
            18: 4,
            19: 7,
            20: 13,
            21: 14,
            22: 12,
            23: 15,
            24: 20,
            25: 23,
            26: 21,
            27: 22,
            28: 28,
            29: 31,
            30: 29,
            31: 30
    }
    chips = []
    for chipid, (x_start, y_start) in zip(chipids,
            product(range(0, nx, Dx), range(0, ny, Dx))):
        subset_pixels = pixel_ids[y_start:y_start+Dy,x_start:x_start+Dx]
        subset_pixels = subset_pixels.reshape(Dx*Dy)
        channel_connections = []
        for channel_id, pixel_id in enumerate(subset_pixels):
            channel_connections.append(subset_pixels[assignments[channel_id]])
        chips.append((chipid, channel_connections))
    return chips
