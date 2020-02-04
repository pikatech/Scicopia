import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scicopia", # Replace with your own username
    version="0.0.1",
    author="Pikatech",
    author_email="pikatech@mail.de",
    description="A search frontend powered by Elasticsearch and Flask.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pikatech/Scicopia",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
