# pdf-color-page-counter

A Python tool to identify and separate colored pages from black & white pages in PDF documents. Perfect for optimizing printing services and cost management.

## Features

- 🎨 Automatically detects colored vs. black & white pages in PDF files
- 🖥️ User-friendly GUI for easy interaction
- 📊 Generates color and B&W page lists in CSV format
- 📄 Splits PDFs into separate color and B&W documents
- ⚡ Fast processing with configurable sensitivity

## Quick Start (No Python Required)

### 📥 Option 1: Download Prebuilt Binary (Easiest)

1. Go to [**Releases**](https://github.com/gamberoillecito/pdf-color-page-counter/releases)
2. Download the archive for your OS:
	- `PDF_Color_Page_Counter-windows-*.exe.zip`
	- `PDF_Color_Page_Counter-macos-*.zip`
	- `PDF_Color_Page_Counter-linux-*.zip`
3. Extract the archive
4. Run the included binary:
	- Windows: double-click `.exe`
	- macOS/Linux: run `chmod +x PDF_Color_Page_Counter*` once, then launch it

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

If using a release binary: extract and run the app executable for your platform.

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
total_pages, color_pages = find_color_pages(pdf_path)
write_split_pdfs(
	input_pdf=pdf_path,
	total_pages=total_pages,
	color_pages=color_pages,
	out_color_pdf=Path("color_pages.pdf"),
	out_bw_pdf=Path("bw_pages.pdf"),
)
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
