from pathlib import Path

from setuptools import setup


def geometric_data_files():
    root = Path('geometric_data')
    directories = sorted({path.parent for path in root.rglob('*.geojson')})
    data_files = []
    for directory in directories:
        files = [str(path) for path in sorted(directory.glob('*.geojson'))]
        target = str(Path('share') / directory)
        data_files.append((target, files))
    return data_files


setup(data_files=geometric_data_files())
