# pdf-color-page-counter

A Python tool to identify and separate colored pages from black & white pages in PDF documents. Perfect for optimizing printing services and cost management.

## Features

- 🎨 Automatically detects colored vs. black & white pages in PDF files
- 🖥️ User-friendly GUI for easy interaction
- 📊 Generates color and B&W page lists in CSV format
- 📄 Splits PDFs into separate color and B&W documents
- ⚡ Fast processing with configurable sensitivity

## Quick Start (Windows - No Python Required!)

### 📥 Option 1: Download Executable (Easiest)

1. Go to [**Releases**](https://github.com/gamberoillecito/pdf-color-page-counter/releases)
2. Download `PDF_Color_Page_Counter.exe`
3. Run it directly - everything is included!

---

## Installation (For Python Users)

### Option 1: Using pip (from source)

Requires: Python 3.11 or higher

```bash
git clone https://github.com/gamberoillecito/pdf-color-page-counter.git
cd pdf-color-page-counter
pip install -r requirements.txt
```

### Option 2: Using setup.py

```bash
git clone https://github.com/gamberoillecito/pdf-color-page-counter.git
cd pdf-color-page-counter
pip install -e .
```

## Usage

### GUI Application

If using Python:
```bash
python pdf_color_bw_gui.py
```

If using the `.exe` file: Just double-click it!

Then:

1. Click "Open PDF..." to select a PDF file
2. The tool will analyze all pages and identify colored ones
3. View results in the GUI and export to CSV or split PDFs

### Command Line (color_page_counter.py)

For advanced users who want to integrate this into scripts:

```python
from color_page_counter import find_color_pages, write_split_pdfs
from pathlib import Path

pdf_path = Path("your_document.pdf")
color_pages, bw_pages = find_color_pages(pdf_path)
write_split_pdfs(pdf_path, color_pages, bw_pages)
```

## Configuration

The color detection algorithm includes tunable parameters:

- `tolerance`: Color channel difference threshold (default: 12)
- `min_color_ratio`: Minimum fraction of colored pixels to classify as colored (default: 0.005)
- `dpi`: DPI for page rendering (default: 50)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Giacomo Bertelli
