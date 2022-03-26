#!/usr/bin/env python
import math
import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from importlib.metadata import Distribution

import nibabel as nib
import numpy.typing as npt

import matplotlib.pyplot as plt
import functools
import operator
from loguru import logger

from chris_plugin import chris_plugin, PathMapper

__pkg = Distribution.from_name(__package__)
__version__ = __pkg.version


DISPLAY_TITLE = r"""
       _                       _                             _
      | |                     (_)                           (_)
 _ __ | |______ _ __ ___  _ __ _ ______ _ __  _ __ _____   ___  _____      __
| '_ \| |______| '_ ` _ \| '__| |______| '_ \| '__/ _ \ \ / / |/ _ \ \ /\ / /
| |_) | |      | | | | | | |  | |      | |_) | | |  __/\ V /| |  __/\ V  V /
| .__/|_|      |_| |_| |_|_|  |_|      | .__/|_|  \___| \_/ |_|\___| \_/\_/
| |                                    | |
|_|                                    |_|                           
"""


parser = ArgumentParser(description='A ChRIS plugin to create brain volume report images',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-b', '--background', default=0.0, type=float,
                    help='threshold indicating background voxels')
parser.add_argument('-p', '--pattern', default='**/*.nii*',
                    help='input file pattern')
parser.add_argument('-o', '--output', default='.png',
                    help='output file extension')
parser.add_argument('-V', '--version', action='version',
                    version=f'$(prog)s {__version__}')


def total_volume(img, threshold: float = 0.0) -> tuple[int, str]:
    """
    :param img: nibabel image
    :param threshold: foreground intensity threshold
    :return: total number of voxels and volume with units
    """
    data = img.get_fdata()
    units, _ = img.header.get_xyzt_units()
    num_voxels = count_positive(data, threshold)
    total_vol = num_voxels * get_voxel_size(img.affine)
    return num_voxels, f'{total_vol:.3f} {units}\u00B3'


def get_voxel_size(affine: npt.NDArray) -> float:
    a3 = (vector_length(affine[i, 0:3]) for i in range(3))
    return abs(functools.reduce(operator.mul, a3, 1))


def vector_length(data: npt.NDArray) -> float:
    return math.sqrt(sum(c ** 2 for c in data))


def count_positive(data: npt.NDArray, threshold: float = 0.0) -> int:
    return (data > threshold).sum()


def slices_figure(data: npt.NDArray, caption: str) -> plt.Figure:
    """
    Display the center slice of each plane in a 3D volumetric image in subfigures,
    with a text caption in quadrant IV.

    :param data: 3D volumetric data
    :param caption: text caption
    :return: matplotlib figure
    """
    if len(data.shape) == 4:
        if data.shape[3] != 1:
            raise ValueError('4D image not supported')
        data = data[:, :, :, 0]

    fig, axes = plt.subplots(2, 2)
    fig.set_size_inches(6, 4)
    x, y, z = data.shape
    slice_0 = data[x // 2, :, :]
    slice_1 = data[:, y // 2, :]
    slice_2 = data[:, :, z // 2]

    axes[0, 0].imshow(slice_0, cmap='gray', origin='lower')
    axes[0, 1].imshow(slice_1, cmap='gray', origin='lower')
    axes[1, 0].imshow(slice_2, cmap='gray', origin='lower')
    axes[1, 1].axis('off')
    axes[1, 1].text(x=0, y=0, s=caption, fontsize='large')
    return fig


@chris_plugin(
    parser=parser,
    title='Brain Volume',
    category='MRI',
    min_memory_limit='500Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    print(DISPLAY_TITLE, file=sys.stderr, flush=True)
    logger.debug('background threshold: {}', options.background)
    mapper = PathMapper(inputdir, outputdir,  suffix=options.output)

    for input_file, output_file in mapper:
        try:
            img = nib.load(input_file)
            data = img.get_fdata()
            num_voxels, total_vol = total_volume(img, options.background)
            text = f'total volume = \n{num_voxels} voxels\n{total_vol}'
            fig = slices_figure(data, text)
            fig.savefig(output_file)
            logger.info('{} -> {}: {} voxels, volume={}', input_file, output_file, num_voxels, total_vol)
        except Exception:
            logger.error('Failed to process {}', input_file)
            raise


if __name__ == '__main__':
    main()