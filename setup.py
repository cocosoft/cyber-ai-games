from setuptools import setup, find_packages

setup(
    name="cyber-ai-games",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "psutil",
    ],
    python_requires=">=3.8",
)
