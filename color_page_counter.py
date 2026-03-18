import argparse
from pathlib import Path

import numpy as np
from PIL import Image
import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter


def is_color_page(
    pil_img: Image.Image,
    tolerance: int = 12,
    min_color_ratio: float = 0.005,
) -> tuple[bool, float]:
    """
    Returns:
      - bool: True if the page is considered color
      - float: fraction of 'colored' pixels
    """
    rgb = np.asarray(pil_img.convert("RGB"), dtype=np.int16)

    # Channel difference: if R,G,B are equal => grayscale pixel
    rg = np.abs(rgb[:, :, 0] - rgb[:, :, 1])
    rb = np.abs(rgb[:, :, 0] - rgb[:, :, 2])
    gb = np.abs(rgb[:, :, 1] - rgb[:, :, 2])

    color_mask = (rg > tolerance) | (rb > tolerance) | (gb > tolerance)
    color_ratio = float(color_mask.mean())

    return color_ratio >= min_color_ratio, color_ratio


def find_color_pages(
    pdf_path: Path,
    dpi: int = 50,
    tolerance: int = 12,
    min_color_ratio: float = 0.005,
    verbose: bool = False,
):
    doc = pdfium.PdfDocument(str(pdf_path))
    color_pages = []

    scale = dpi / 72.0  # PDF base is 72 DPI

    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=scale)
        pil_img = bitmap.to_pil()

        is_color, ratio = is_color_page(
            pil_img, tolerance=tolerance, min_color_ratio=min_color_ratio
        )
        if is_color:
            color_pages.append(i + 1)  # 1-based page index

        if verbose:
            print(
                f"Page {i+1:>4}: "
                f"{'COLOR' if is_color else 'B/W'} "
                f"(color pixels: {ratio*100:.3f}%)"
            )

    return len(doc), color_pages


def write_split_pdfs(
    input_pdf: Path,
    total_pages: int,
    color_pages: list[int],
    out_color_pdf: Path | None = None,
    out_bw_pdf: Path | None = None,
):
    if out_color_pdf is None and out_bw_pdf is None:
        return

    reader = PdfReader(str(input_pdf))
    color_set = set(color_pages)

    if out_color_pdf is not None:
        out_color_pdf.parent.mkdir(parents=True, exist_ok=True)
        color_writer = PdfWriter()
        for i in range(total_pages):
            if (i + 1) in color_set:
                color_writer.add_page(reader.pages[i])
        with out_color_pdf.open("wb") as f:
            color_writer.write(f)
        print(f"Written color PDF: {out_color_pdf}")

    if out_bw_pdf is not None:
        out_bw_pdf.parent.mkdir(parents=True, exist_ok=True)
        bw_writer = PdfWriter()
        for i in range(total_pages):
            if (i + 1) not in color_set:
                bw_writer.add_page(reader.pages[i])
        with out_bw_pdf.open("wb") as f:
            bw_writer.write(f)
        print(f"Written B/W PDF: {out_bw_pdf}")


def main():
    parser = argparse.ArgumentParser(
        description="Count and list color pages in a PDF."
    )
    parser.add_argument("pdf", type=Path, help="Path to the PDF file")
    parser.add_argument("--dpi", type=int, default=50, help="Render DPI (default: 50)")
    parser.add_argument(
        "--tolerance",
        type=int,
        default=12,
        help="RGB channel-difference threshold to mark a pixel as colored (default: 12)",
    )
    parser.add_argument(
        "--min-color-ratio",
        type=float,
        default=0.002,
        help="Minimum fraction of colored pixels to mark a page as color (default: 0.002 = 0.2%%)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show per-page details",
    )
    parser.add_argument(
        "--out-color-pdf",
        type=Path,
        default=None,
        help="Optional output PDF path containing only color pages",
    )
    parser.add_argument(
        "--out-bw-pdf",
        type=Path,
        default=None,
        help="Optional output PDF path containing only B/W pages",
    )

    args = parser.parse_args()

    if not args.pdf.exists():
        raise FileNotFoundError(f"File not found: {args.pdf}")

    total_pages, color_pages = find_color_pages(
        args.pdf,
        dpi=args.dpi,
        tolerance=args.tolerance,
        min_color_ratio=args.min_color_ratio,
        verbose=args.verbose,
    )

    color_set = set(color_pages)
    bw_pages = [i for i in range(1, total_pages + 1) if i not in color_set]

    print(f"\nTotal pages:t{total_pages}")
    print(f"Color pages: {len(color_pages)}")
    print(f"BW pages: {len(bw_pages)}")
    print("Color page list:\n", ",".join(map(str, color_pages)) if color_pages else "none")
    print("BW page list:\n", ",".join(map(str, bw_pages)) if bw_pages else "none")

    write_split_pdfs(
        input_pdf=args.pdf,
        total_pages=total_pages,
        color_pages=color_pages,
        out_color_pdf=args.out_color_pdf,
        out_bw_pdf=args.out_bw_pdf,
    )


if __name__ == "__main__":
    main()