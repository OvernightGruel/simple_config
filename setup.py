import setuptools
import simple_config

with open('README.md', 'r', encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple_config",
    version=simple_config.__version__,
    author="clay",
    author_email="zhouweiqi@situdata.com",
    description="A small tool to parse and store project config",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
