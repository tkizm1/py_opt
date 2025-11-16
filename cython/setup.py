# setup.py

from setuptools import setup,Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(Extension(name='kmp_cython',sources=["kmp_cython.pyx"]))
)