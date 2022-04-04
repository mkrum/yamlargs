import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yamlargs",
    description="YAML based config management for ML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.1.7",
    packages=["yamlargs"],
    python_requires=">=3",
    install_requires=["pyyaml"],
)
