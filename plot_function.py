#!/usr/bin/env python
"""
This script demonstrates how to use matplotlib for 2d or 3d colormaps
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob
import os
from scipy.ndimage.interpolation import map_coordinates


def main():
    # some parameters
    npts_real = 400
    npts_imag = 400
    realaxis = np.linspace(-4, 4, npts_real)
    imagaxis = np.linspace(-3, 3, npts_imag)
    regrid, imgrid = np.meshgrid(realaxis, imagaxis)

    # put complex magnitude and argument in 2d array
    zgrid = regrid + 1j * imgrid
    # complex_sine = np.sin(regrid + 1j * imgrid)
    # no branch cut:
    complex_function = (zgrid ** 2 - 2.) * (zgrid - 1 - 1j) ** 2 /\
                       (zgrid + 2j) / (zgrid**2 - 5 - 2j)
    # with branch cut:
    #complex_function = np.arcsin(zgrid)

    data = np.empty((2, npts_imag, npts_real))
    data[0] = np.log(np.abs(complex_function))
    data[1] = np.angle(complex_function)

    # normalize array
    drange = np.abs(data[0]).max() / 2.
    norm0 = plt.Normalize(-drange, drange)
    norm1 = plt.Normalize(-np.pi, np.pi)
    data[0] = norm0(data[0])
    data[1] = norm1(data[1])

    paths_cmap = glob.glob('colormap2d/colormaps/*.npy')
    ncmaps = len(paths_cmap) + 1  # one extra cmap for hsv
    fig, axes = plt.subplots(ncmaps, 2, figsize=(10, ncmaps * 3))
    fig.suptitle('colormap comparison using complex polynomial:\n'
                 r'$f(z) = \frac{(z^2-2)(z-(1+i))^2}{(z+2i)(z^2-(5+2i))}$',
                 fontsize=16)

    # hsv colormap
    ax20, ax21 = axes[0, 0], axes[0, 1]
    ax20.set(ylabel='{}\nlog(|f|)'.format('HSV colormap'),
             xlabel='arg(f)')
    ax21.set(ylabel='imaginary axis',
             xlabel='real axis')

    xx, yy = np.meshgrid(np.linspace(0., 1., 100), np.linspace(0., 1., 100))
    cmap_grid = np.array([yy, xx])
    cmap = cmap_multidim_hsv(cmap_grid)
    cmap = np.roll(cmap, 48, axis=1)
    rgb_colors = cmap_file2d(data, cmap)

    ax20.imshow(cmap, aspect='auto', extent=(-np.pi, np.pi, -drange, drange),
                origin='lower')
    ax21.imshow(rgb_colors, aspect='auto', extent=(-4, 4, -3, 3),
                origin='lower')

    for path_cmap, (col1, col2) in zip(paths_cmap, axes[1:]):
        dirname, fname = os.path.split(path_cmap)
        cmap = np.load(path_cmap).transpose((1, 0, 2))
        # ihalf = int(cmap.shape[0] * 0.5)
        # cmap = cmap[::-1]
        # cmap = cmap[:ihalf]
        col1.set(ylabel='{}\nlog(|f|)'.format(fname),
                 xlabel='arg(f)')
        col2.set(ylabel='imaginary axis',
                 xlabel='real axis')

        rgb_colors = cmap_file2d(data, cmap)

        col1.imshow(cmap, aspect='auto', origin='lower',
                    extent=(-np.pi, np.pi, -drange, drange))
        col2.imshow(rgb_colors, aspect='auto', extent=(-4, 4, -3, 3),
                    origin='lower')

    fig.tight_layout(pad=0.5)
    fig.subplots_adjust(top=0.9)
    plt.show()


def cmap_multidim_hsv(data, mapping={'sat': 0, 'hue': 1, 'val': 0}):
    ihue = mapping['hue']
    if isinstance(ihue, basestring):
        fill_value = float(ihue.strip('_fill'))
        hue = np.ones_like(data[0]) * fill_value
    else:
        hue = data[ihue]
    isat = mapping['sat']
    if isinstance(isat, basestring):
        fill_value = float(isat.strip('_fill'))
        sat = np.ones_like(data[0]) * fill_value
    else:
        sat = data[isat]
    ival = mapping['val']
    if isinstance(ival, basestring):
        fill_value = float(ival.strip('_fill'))
        val = np.ones_like(data[0]) * fill_value
    else:
        val = data[ival]

    hsvcolors = np.array([(-hue + 0.4) % 1.0, sat, val]).T
    rgb = mpl.colors.hsv_to_rgb(hsvcolors).transpose((1, 0, 2))
    return rgb


def cmap_file2d(data, cmap, roll_x=0.):
    cmap[:, -1] = cmap[:, 0]
    data_dim, nrows, ncols = data.shape
    data2 = np.copy(data)
    #data2[1] = (data2[1] - roll_x) % 1.0
    data2[0] *= cmap.shape[0]
    data2[1] *= cmap.shape[1]
    data2 = data2.reshape(data_dim, nrows, ncols)
    r = map_coordinates(cmap[:, :, 0], data2, order=1, mode='nearest')
    g = map_coordinates(cmap[:, :, 1], data2, order=1, mode='nearest')
    b = map_coordinates(cmap[:, :, 2], data2, order=1, mode='nearest')
    rgb = np.array([r, g, b])
    rgb = rgb.reshape(3, nrows, ncols).transpose(1, 2, 0)

    return rgb


if __name__ == "__main__":
    main()
