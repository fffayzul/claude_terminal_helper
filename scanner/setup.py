from setuptools import setup, Extension

setup(
    name="scanner",
    ext_modules=[
        Extension(
            name="scanner",
            sources=["scanner.c"],
        )
    ],
)
