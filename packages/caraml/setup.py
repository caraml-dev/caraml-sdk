import setuptools
import pathlib
import pkg_resources

with pathlib.Path("version.py").open() as version_py:
    _locals = locals()
    exec(version_py.read(), globals(), _locals)
    version = _locals["VERSION"]

with pathlib.Path("requirements.txt").open() as requirements_txt:
    requirements = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

with pathlib.Path("requirements.dev.txt").open() as dev_requirements_test:
    dev_requirements = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(dev_requirements_test)
    ]

setuptools.setup(
    name="caraml",
    version=version,
    packages=setuptools.find_packages(),
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    python_requires=">=3.9,<3.14",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
)
