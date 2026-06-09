from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name             = "agentlens",
    version          = "0.1.0",
    description      = "Zero-dependency audit trail for AI agents",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author           = "schnnjuan",
    author_email     = "sant012@icloud.com",
    url              = "https://github.com/schnnjuan/agentlens",
    packages         = find_packages(),
    python_requires  = ">=3.8",
    install_requires = [],          # zero dependencies — this is the whole point
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agents audit logging compliance identity governance",
)
