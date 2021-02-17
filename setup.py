import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyAedatTools-believeinlain", # Replace with your own username
    version="0.1.0",
    author="Stephanie Aelmore",
    author_email="steph.aelmore@gmail.com",
    description="Tools for importing AEDAT files into numpy arrays.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/believeinlain/PyAedatTools/tree/import-only",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7.9',
)