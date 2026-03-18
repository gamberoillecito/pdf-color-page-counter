from setuptools import setup, find_packages

setup(
    name="pdf-color-page-counter",
    version="0.1.0",
    description="A simple tool to identify colored pages in PDF for printing services",
    author="Giacomo Bertelli",
    license="MIT",
    py_modules=["color_page_counter", "pdf_color_bw_gui"],
    python_requires=">=3.11",
    install_requires=[
        "pillow>=10.0.0",
        "pypdfium2>=4.0.0",
        "pypdf>=4.0.0",
        "numpy>=1.24.0",
    ],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
    ],
)
