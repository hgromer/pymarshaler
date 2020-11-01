import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymarshall",
    version="0.1.4",
    author="Hernan Romer",
    author_email="nanug33@gmail.com",
    description="Package to pymarshall/unmarshall python objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hgromer/pymarshall",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
