#!/usr/bin/env python3
"""Tidy a raw SLAM map: crop to the room, fill speckle, solidify obstacles."""
import sys
from collections import deque
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
MIN_OBSTACLE = int(sys.argv[3]) if len(sys.argv) > 3 else 10

im = Image.open(src).convert('L')
w, h = im.size
px = im.load()
OCC, FREE, UNK = 0, 254, 205

N8 = ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1))
N4 = ((1,0),(-1,0),(0,1),(0,-1))

def components(match, nbrs, box=None):
    x0, y0, x1, y1 = box if box else (0, 0, w - 1, h - 1)
    seen, comps = set(), []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in seen or not match(x, y):
                continue
            q, comp = deque([(x, y)]), []
            seen.add((x, y))
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for dx, dy in nbrs:
                    nx, ny = cx + dx, cy + dy
                    if (x0 <= nx <= x1 and y0 <= ny <= y1
                            and (nx, ny) not in seen and match(nx, ny)):
                        seen.add((nx, ny)); q.append((nx, ny))
            comps.append(comp)
    return comps

# 1. Find the room: biggest black shape is the outer wall
black = components(lambda x, y: px[x, y] < 50, N8)
walls = max(black, key=len)
xs = [p[0] for p in walls]; ys = [p[1] for p in walls]
box = (min(xs), min(ys), max(xs), max(ys))
print('room bbox', box, 'wall pixels', len(walls))

# 2. Keep walls and black shapes bigger than the noise threshold
occ = set(walls)
kept = 1
for c in black:
    if c is not walls and len(c) > MIN_OBSTACLE:
        occ.update(c); kept += 1
print('black shapes kept', kept, 'of', len(black))

# 3. Non-black regions inside the room: the largest is open floor,
#    any other (enclosed by an obstacle outline) is a solid object interior
rest = components(lambda x, y: (x, y) not in occ, N4, box)
rest.sort(key=len, reverse=True)
floor = set(rest[0])
interiors = [c for c in rest[1:]]
print('open floor px', len(floor), 'enclosed interiors', len(interiors))
for c in interiors:
    occ.update(c)

# 4. Write the cleaned map
out = Image.new('L', (w, h), UNK)
o = out.load()
for y in range(box[1], box[3] + 1):
    for x in range(box[0], box[2] + 1):
        o[x, y] = OCC if (x, y) in occ else FREE
out.save(dst)
print('saved', dst)
