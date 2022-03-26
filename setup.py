from setuptools import setup

setup(
    name='mri-preview',
    version='1.0.0',
    description='A ChRIS plugin to preview the center slices of MRI',
    author='Jennings Zhang',
    author_email='Jennings.Zhang@childrens.harvard.edu',
    url='https://github.com/FNNDSC/pl-mri-preview',
    py_modules=['mri_preview'],
    install_requires=['chris_plugin', 'nibabel', 'matplotlib', 'loguru'],
    license='MIT',
    python_requires='>=3.10.2',
    entry_points={
        'console_scripts': [
            'mri_preview = mri_preview:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
