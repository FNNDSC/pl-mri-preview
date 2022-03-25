from setuptools import setup

setup(
    name='stamp-volume',
    version='1.0.0',
    description='A ChRIS plugin to create brain volume report images',
    author='FNNDSC',
    author_email='Jennings.Zhang@childrens.harvard.edu',
    url='https://github.com/FNNDSC/pl-stamp-volume',
    py_modules=['stampvolume'],
    install_requires=['chris_plugin'],
    license='MIT',
    python_requires='>=3.8.2',
    entry_points={
        'console_scripts': [
            'stampvolume = stampvolume:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
