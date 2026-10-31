#!/usr/bin/env python3
"""Tidy a raw SLAM map: crop to the room, fill speckle, solidify obstacles.

Usage: clean_map.py RAW.pgm CLEAN.pgm [MIN_OBSTACLE_PIXELS]
"""
import argparse
from collections import deque

from PIL import Image

OCCUPIED, FREE, UNKNOWN = 0, 254, 205

NEIGHBOURS_8 = ((1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (-1, -1), (1, -1), (-1, 1))
NEIGHBOURS_4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def components(size, match, neighbours, box=None):
    """Flood-fill every connected region of pixels where match(x, y) is true."""
    w, h = size
    x0, y0, x1, y1 = box if box else (0, 0, w - 1, h - 1)
    seen, regions = set(), []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in seen or not match(x, y):
                continue
            queue, region = deque([(x, y)]), []
            seen.add((x, y))
            while queue:
                cx, cy = queue.popleft()
                region.append((cx, cy))
                for dx, dy in neighbours:
                    nx, ny = cx + dx, cy + dy
                    if (x0 <= nx <= x1 and y0 <= ny <= y1
                            and (nx, ny) not in seen and match(nx, ny)):
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            regions.append(region)
    return regions


def clean(src, dst, min_obstacle):
    image = Image.open(src).convert('L')
    pixels = image.load()

    # The largest black shape is the outer wall; its bounding box is the room.
    black = components(image.size, lambda x, y: pixels[x, y] < 50, NEIGHBOURS_8)
    walls = max(black, key=len)
    xs = [p[0] for p in walls]
    ys = [p[1] for p in walls]
    box = (min(xs), min(ys), max(xs), max(ys))
    print('room bbox', box, 'wall pixels', len(walls))

    # Keep the walls and any black shape larger than the noise threshold.
    occupied = set(walls)
    kept = 1
    for shape in black:
        if shape is not walls and len(shape) > min_obstacle:
            occupied.update(shape)
            kept += 1
    print('black shapes kept', kept, 'of', len(black))

    # Inside the room, the largest non-black region is open floor. Any other
    # region is enclosed by an obstacle outline, so it is the object's interior.
    rest = components(image.size, lambda x, y: (x, y) not in occupied,
                      NEIGHBOURS_4, box)
    rest.sort(key=len, reverse=True)
    interiors = rest[1:]
    print('open floor px', len(rest[0]), 'enclosed interiors', len(interiors))
    for region in interiors:
        occupied.update(region)

    out = Image.new('L', image.size, UNKNOWN)
    out_pixels = out.load()
    for y in range(box[1], box[3] + 1):
        for x in range(box[0], box[2] + 1):
            out_pixels[x, y] = OCCUPIED if (x, y) in occupied else FREE
    out.save(dst)
    print('saved', dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('src', help='raw map image (.pgm)')
    parser.add_argument('dst', help='where to write the cleaned map')
    parser.add_argument('min_obstacle', nargs='?', type=int, default=10,
                        help='smallest black shape (in pixels) to keep')
    args = parser.parse_args()
    clean(args.src, args.dst, args.min_obstacle)


if __name__ == '__main__':
    main()
