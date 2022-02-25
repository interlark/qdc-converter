from setuptools import setup, find_packages
import os

here = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

with open(os.path.join(here, 'readme.md')) as f:
    long_description = f.read()

setup(
    name='qdc-converter',
    description='Garmin QDC (Quickdraw Contours) Converter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='qdc garmin converter',
    author_email='interlark@gmail.com',
    url='http://github.com/interlark/qdc-converter',
    version='1.0',
    packages=find_packages(),
    install_requires=install_requires,
    scripts=['qdc-converter'],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
)
