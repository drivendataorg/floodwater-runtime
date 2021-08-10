# adapted from pangeo https://github.com/pangeo-data/pangeo-docker-images/blob/master/tests/test_pangeo-notebook.py
import pytest
import importlib

packages = [
    # these are problem libraries that don't always seem to import, mostly due
    # to dependencies outside the python world
    "rasterio",
    "xarray",
    "fastai",
    "pandas",
    "numpy",
    "torch",  # pytorch
    "sklearn",  # scikit-learn
    "scipy",
    "xgboost",
    "tensorflow"
]


@pytest.mark.parametrize("package_name", packages, ids=packages)
def test_import(package_name):
    importlib.import_module(package_name)
