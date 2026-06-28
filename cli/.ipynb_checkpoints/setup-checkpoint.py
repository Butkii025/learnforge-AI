from setuptools import setup

setup(
    name="learnforge-cli",
    version="0.1.0",
    py_modules=["learnforge_cli"],
    install_requires=[],
    entry_points={
        "console_scripts": [
            "learnforge=learnforge_cli:main",
        ],
    },
)
