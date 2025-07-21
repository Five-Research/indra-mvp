from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="indra-mvp",
    version="0.1.0",
    description="AI Agent Orchestration Framework - MVP",
    author="Mehul - Five Labs",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "indra=indra.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)