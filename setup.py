from pathlib import Path

from setuptools import setup

PLUGIN_NAME = 'pytest-cairo'
SOURCE = 'pytest_cairo'

setup(
    name=PLUGIN_NAME,
    description='Pytest support for cairo-lang and starknet',
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/TimNooren/pytest-cairo',
    packages=[SOURCE],
    version='0.0.1',
    # Make the plugin available to pytest:
    entry_points={'pytest11': [f'{PLUGIN_NAME} = {SOURCE}.plugin']},
    # PyPI classifier for pytest plugins:
    classifiers=['Framework :: Pytest'],
    install_requires=[
        'cairo-lang',
        'pytest',
    ],
    python_requires='>=3.7',
)
