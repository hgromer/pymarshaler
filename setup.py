import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="pymarshaler",
    version="0.2.2",
    author="Hernan Romer",
    author_email="nanug33@gmail.com",
    description="Package to marshal and unmarshal python objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hgromer/pymarshaler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    python_requires='>=3.7',
)
