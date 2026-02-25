"""
Setup script for Vietnamese Normalizer package.
"""

from setuptools import setup, find_namespace_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="vietnormalizer",
    version="0.2.1",
    description="A Python library for normalizing Vietnamese text for TTS and NLP applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nghi Studio",
    author_email="nghimestudio@gmail.com",
    url="https://github.com/nghimestudio/vietnormalizer",
    packages=find_namespace_packages(),
    package_data={
        "vietnormalizer": ["data/*.csv"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["vietnamese", "text-normalization", "nlp", "tts", "text-to-speech"],
    zip_safe=False,
)

