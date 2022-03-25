#!/usr/bin/env python

import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from importlib.metadata import Distribution

from chris_plugin import chris_plugin

__pkg = Distribution.from_name(__package__)
__version__ = __pkg.version


DISPLAY_TITLE = r"""
       _            _                                         _                      
      | |          | |                                       | |                     
 _ __ | |______ ___| |_ __ _ _ __ ___  _ __ ________   _____ | |_   _ _ __ ___   ___ 
| '_ \| |______/ __| __/ _` | '_ ` _ \| '_ \______\ \ / / _ \| | | | | '_ ` _ \ / _ \
| |_) | |      \__ \ || (_| | | | | | | |_) |      \ V / (_) | | |_| | | | | | |  __/
| .__/|_|      |___/\__\__,_|_| |_| |_| .__/        \_/ \___/|_|\__,_|_| |_| |_|\___|
| |                                   | |                                            
|_|                                   |_|                                            
"""


parser = ArgumentParser(description='A ChRIS plugin to create brain volume report images',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-e', '--example', default='jelly',
                    help='argument which does not do anything')
parser.add_argument('-V', '--version', action='version',
                    version=f'$(prog)s {__version__}')


# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='Brain Volume',
    category='',                 # ref. https://chrisstore.co/plugins
    min_memory_limit='100Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0              # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    print(DISPLAY_TITLE, file=sys.stderr)
    print(f'Option: {options.example}', file=sys.stderr)


if __name__ == '__main__':
    main()

