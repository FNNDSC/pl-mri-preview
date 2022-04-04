#!/usr/bin/env python
import math
import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from importlib.metadata import Distribution
from typing import Iterable

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
parser.add_argument('-i', '--inputs', default='.nii,.nii.gz,.mnc,.mgz',
                    help='file extension of input files, comma-separated')
parser.add_argument('-o', '--outputs', default='.png,.txt',
                    help='output file extensions, comma-separated')
parser.add_argument('-u', '--units-fallback', type=str, default='unknown', dest='units_fallback',
                    help='voxel size units for file formats where units are unknown')
parser.add_argument('-V', '--version', action='version',
                    version=f'$(prog)s {__version__}')


def total_volume(img, threshold: float = 0.0) -> tuple[int, float]:
    """
    :param img: nibabel image
    :param threshold: foreground intensity threshold
    :return: total number of voxels, volume, and cubic units of the volume
    """
    data = img.get_fdata()
    num_voxels = count_positive(data, threshold)
    total_vol = num_voxels * get_voxel_size(img)
    return num_voxels, total_vol


def get_voxel_size(img) -> float:
    return abs(functools.reduce(operator.mul, img.header.get_zooms(), 1))


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


def multi_mapper(inputdir: Path, outputdir: Path, file_extensions: str) -> Iterable[tuple[Path, Path]]:
    for file_extension in file_extensions.split(','):
        yield from PathMapper(
            inputdir, outputdir,
            glob=f'**/*{file_extension}',
            name_mapper=_gz_aware_placeholder_mapper,
            fail_if_empty=False
        )


def _gz_aware_placeholder_mapper(input_file: Path, output_dir: Path) -> Path:
    filename = str(input_file)
    if filename.endswith('.gz'):
        filename = filename[:-3] + '_gz'
    if '.' not in filename:
        raise ValueError(f'Unrecognized file extension in: {input_file}')
    return (output_dir / filename).with_suffix('.out')


def save_as(img, output: Path, num_voxels: int, total_vol: float, units: str) -> None:
    if output.name.endswith('.txt'):
        with output.open('w') as f:
            f.write(f'{num_voxels} voxels\n{total_vol} {units}^3')
    else:
        text = f'total volume = \n{num_voxels:,} voxels\n{total_vol:,.1f} {units}\u00B3'
        fig = slices_figure(img.get_fdata(), text)
        fig.savefig(output)


@chris_plugin(
    parser=parser,
    title='Brain Volume',
    category='MRI',
    min_memory_limit='500Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    print(DISPLAY_TITLE, file=sys.stderr, flush=True)
    logger.debug('input files: {}', options.inputs.split(','))
    logger.debug('output formats: {}', options.outputs.split(','))
    logger.debug('background threshold: {}', options.background)
    mapper = multi_mapper(inputdir, outputdir, options.inputs)

    for input_file, output_base in mapper:
        try:
            img = nib.load(input_file)
            num_voxels, total_vol = total_volume(img, options.background)

            if hasattr(img.header, 'get_xyzt_units') and callable(img.header.get_xyzt_units):
                units, _ = img.header.get_xyzt_units()
            else:
                logger.error('Not supported for {}', type(img.header))
                units = options.units_fallback

            logger.info('{}: {} voxels, volume={} {}^3', input_file, num_voxels, total_vol, units)
            for output_ext in options.outputs.split(','):
                output_file = output_base.with_suffix(output_ext)
                save_as(img, output_file, num_voxels, total_vol, units)
                logger.info('\t-> {}', output_file)
        except Exception:
            logger.error('Failed to process {}', input_file)
            raise


if __name__ == '__main__':
    main()
