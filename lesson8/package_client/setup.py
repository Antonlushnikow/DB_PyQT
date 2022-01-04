import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="messenger-al-client",
    version="0.0.5",
    author="Anton Lushnikov",
    author_email="antonlushnikow@gmail.com",
    description="Messenger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Antonlushnikow/DB_PyQT",
    project_urls={
        "Bug Tracker": "https://github.com/Antonlushnikow/DB_PyQT/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'PyQT5',
        'pycryptodome',
        'sqlalchemy'
    ],
    python_requires=">=3.6",
)