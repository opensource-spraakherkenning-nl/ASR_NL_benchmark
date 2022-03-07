import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

with open((HERE / "requirements.txt"), 'r') as fh:
    requirements = [r.split('#', 1)[0].strip() for r in fh.read().split('\n')]

# This call to setup() does all the work
setuptools.setup(
    name="ASR_NL_benchmark",
    version="0.0.1",
    description="A benchmarker for Speach-to-text",
    long_description=README,
    long_description_content_type="text/x-md",
    url="https://github.com/opensource-spraakherkenning-nl/ASR_NL_benchmark",
    author="Rana Klein",
    author_email="rklein@beeldengeluid.nl",
    classifiers=[
        "Programming Language :: Python"
    ],
    package_dir={'Package': 'ASR_NL_benchmark'},
    packages=setuptools.find_packages(include=['ASR_NL_benchmark', 'ASR_NL_benchmark.*']),
    python_requires=">=3",
    include_package_data=True,
    package_data={'ASR_NL_benchmark':['templates/*.html','data/*']},
    install_requires=requirements
)