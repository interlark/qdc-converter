import distutils.cmd
import os
import re
import sys

from setuptools import find_packages, setup


here = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'qdc_converter', 'version.py')) as f:
    match = re.search(r"^version\s*=\s*'(?P<version>.+?)'", f.read(), re.M)
    assert match
    VERSION = match.group('version')

deps = [
    'numpy>=1.19.0',
    'tqdm>=4.37.0',
    'click>=4.0.0',
    'click-option-group>=0.5.3',
]


class BuildStandaloneCommand(distutils.cmd.Command):
    """A custom command to build standalone app."""
    description = 'Build standalone app with PyInstaller'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import shutil
        import subprocess

        try:
            # Target filename
            dist_filename = 'QDCConverter'

            # Dist
            build_cmd = [
                'pyinstaller',
                '--clean',
                '--onefile',
                '--windowed',
                '-n', dist_filename,
            ]

            # Icon
            if sys.platform.startswith('win'):
                build_cmd += [
                    '--icon', 'qdc_converter/data/images/icon.ico',
                ]
            elif sys.platform.startswith('darwin'):
                build_cmd += [
                    '--icon', 'qdc_converter/data/images/icon.icns',
                ]

            # Add data
            build_cmd += [
                '--add-data', f'qdc_converter/data{os.pathsep}qdc_converter/data',
                'qdc-converter.py',
            ]

            print('Running command: %s' % ' '.join(build_cmd), file=sys.stderr)
            subprocess.check_call(build_cmd)
        finally:
            # Cleanup
            shutil.rmtree(os.path.join(here, 'build'), ignore_errors=True)
            try:
                os.remove(os.path.join(here, f'{dist_filename}.spec'))
            except FileNotFoundError:
                pass


setup(
    name='qdc-converter',
    description='Garmin QDC (Quickdraw Contours) Converter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='qdc garmin converter',
    author='Andy Trofimov',
    author_email='interlark@gmail.com',
    url='http://github.com/interlark/qdc-converter',
    version=VERSION,
    python_requires='>=3.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=deps,
    extras_require={
        'gui': [
            'PySimpleGUI==4.60.0',
        ],
        'dev': [
            'pyinstaller>=5.0',
            'wheel>=0.36.2,<0.38',
            'pre-commit>=2.6',
            'pytest>=6.2,<8',
        ],
    },
    license='MIT',
    entry_points={'console_scripts': ['qdc-converter = qdc_converter:main']},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    cmdclass={'build_standalone': BuildStandaloneCommand},
)
