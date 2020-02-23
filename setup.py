import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yamlreader",
    version="3.0.5",
    author="Schlomo Schapiro, Jędrzej Orbik",
    author_email="jendker@users.noreply.github.com",
    description="Merge YAML data from given files, dir or file glob",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license = 'Apache License 2.0',
    url="https://github.com/Jendker/yamlreader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires = [
            'ruamel.yaml'
    ],
    python_requires='>=3.6',
)