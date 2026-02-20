import math


def fast_mul(a, b):
    result = 0
    
    while b > 0:
        if b % 2 == 1:
            result += a
        a *= 2
        b //= 2
    
    return result


def fast_pow(a, b):
    temp = a
    for i in range(b-1):
        temp = fast_mul(temp, a)
    return temp

def na15(x):
    tx = x+x
    fx = tx + tx
    ex = fx + fx
    msx = x - ex 
    ffx = ex - msx
    return ffx

def fast_mul_gen(y):
    print('''
a = int(input())
b = int(input())
if y == 12:
    a = x + x
    b = a + a
    c = b + b
    d = c + b
    print(d)
elif y == 16:
    a = x + x
    b = a + a
    c = b + b
    d = c + c
    print(d)
elif y == 15:
    a = x + x
    b = a + a
    c = b + b
    d = x - c
    e = c - d
    print(e)
else:
    print(None)
    ''')
    return 0


import math
import tkinter as tk

def draw(shader, width, height):
    image = bytearray((0, 0, 0) * width * height)
    for y in range(height):
        for x in range(width):
            pos = (width * y + x) * 3
            color = shader(x / width, y / height)
            normalized = [max(min(int(c * 255), 255), 0) for c in color]
            image[pos:pos + 3] = normalized
    header = bytes(f'P6\n{width} {height}\n255\n', 'ascii')
    return header + image


def main(shader):
    label = tk.Label()
    img = tk.PhotoImage(data=draw(shader, 256, 256)).zoom(2, 2)
    label.pack()
    label.config(image=img)
    tk.mainloop()


def noise(x, y):
    return (math.sin(x * 127.1 + y * 311.7) * 43758.5453) % 1

def lerp(a, b, t):
    return a + t * (b - a)

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def value_noise(x, y, scale):
    gx = x / scale
    gy = y / scale

    x0 = int(gx)
    x1 = x0 + 1
    y0 = int(gy)
    y1 = y0 + 1

    sx = fade(gx - x0)
    sy = fade(gy - y0)

    n0 = lerp(noise(y0, x0), noise(y0, x1), sx)
    n1 = lerp(noise(y1, x0), noise(y1, x1), sx)
    return lerp(n0, n1, sy)


def fractal_noise(
    width,
    height,
    octaves=1,
    persistence=0.5,
    lacunarity=4.0,
    base_scale=0.1,
):
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0
    value = 0
    for _ in range(octaves):
        scale = max(1, int(base_scale / frequency))
        layer = value_noise(width, height, scale)
        value += layer * amplitude

        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return value / max_amplitude

def shader(x, y):
    return fractal_noise(x, y), fractal_noise(x, y), fractal_noise(x, y)
main(shader)