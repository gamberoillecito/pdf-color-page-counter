import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from PIL import Image, ImageTk
import pypdfium2 as pdfium

# Reuse your existing logic from conta_pagine.py
from color_page_counter import find_color_pages, write_split_pdfs


class PdfColorBwGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Color/BW Analyzer")
        self.geometry("1200x760")
        self.minsize(1000, 680)

        self.pdf_path: Path | None = None
        self.total_pages = 0
        self.color_pages: list[int] = []
        self.bw_pages: list[int] = []

        self._preview_photo = None
        self._preview_pil: Image.Image | None = None
        self._current_page_num: int | None = None
        self._current_category: str = ""

        self.color_csv_var = tk.StringVar(value="")
        self.bw_csv_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.file_var = tk.StringVar(value="No PDF selected")
        ttk.Button(top, text="Open PDF...", command=self.open_pdf).pack(side="left")
        ttk.Label(top, textvariable=self.file_var, padding=(10, 0)).pack(side="left", fill="x", expand=True)

        params = ttk.LabelFrame(self, text="Parameters", padding=10)
        params.pack(fill="x", padx=10, pady=(0, 10))

        self.dpi_var = tk.IntVar(value=50)
        self.tolerance_var = tk.IntVar(value=12)
        self.min_ratio_var = tk.DoubleVar(value=0.002)

        ttk.Label(params, text="DPI").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(params, from_=20, to=300, textvariable=self.dpi_var, width=8).grid(row=0, column=1, sticky="w", padx=(6, 20))

        ttk.Label(params, text="Tolerance").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(params, from_=0, to=100, textvariable=self.tolerance_var, width=8).grid(row=0, column=3, sticky="w", padx=(6, 20))

        ttk.Label(params, text="Min color ratio").grid(row=0, column=4, sticky="w")
        ttk.Entry(params, textvariable=self.min_ratio_var, width=10).grid(row=0, column=5, sticky="w", padx=(6, 20))

        ttk.Button(params, text="Analyze", command=self.analyze).grid(row=0, column=6, sticky="w")
        ttk.Button(params, text="Export split PDFs...", command=self.export_split_pdfs).grid(row=0, column=7, sticky="w", padx=(8, 0))

        stats = ttk.Frame(self, padding=(10, 0, 10, 10))
        stats.pack(fill="x")

        self.stats_var = tk.StringVar(value="Total: 0   Color: 0   B/W: 0")
        ttk.Label(stats, textvariable=self.stats_var, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        copy_frame = ttk.Frame(stats)
        copy_frame.pack(fill="x", pady=(6, 0))

        ttk.Label(copy_frame, text="Color CSV:").grid(row=0, column=0, sticky="w")
        ttk.Entry(copy_frame, textvariable=self.color_csv_var).grid(row=0, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(copy_frame, text="Copy color list", command=self.copy_color_csv).grid(row=0, column=2, padx=(0, 12))

        ttk.Label(copy_frame, text="B/W CSV:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(copy_frame, textvariable=self.bw_csv_var).grid(row=1, column=1, sticky="ew", padx=(6, 6), pady=(6, 0))
        ttk.Button(copy_frame, text="Copy B/W list", command=self.copy_bw_csv).grid(row=1, column=2, pady=(6, 0))

        copy_frame.columnconfigure(1, weight=1)

        main = ttk.Panedwindow(self, orient="horizontal")
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(main, padding=8)
        right = ttk.Frame(main, padding=8)
        main.add(left, weight=1)
        main.add(right, weight=2)

        # Left: lists
        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True)

        color_box_frame = ttk.LabelFrame(list_frame, text="Color pages", padding=8)
        color_box_frame.pack(fill="both", expand=True, pady=(0, 8))
        self.color_list = tk.Listbox(color_box_frame, exportselection=False)
        self.color_list.pack(fill="both", expand=True)
        self.color_list.bind("<<ListboxSelect>>", self.on_color_select)

        bw_box_frame = ttk.LabelFrame(list_frame, text="B/W pages", padding=8)
        bw_box_frame.pack(fill="both", expand=True)
        self.bw_list = tk.Listbox(bw_box_frame, exportselection=False)
        self.bw_list.pack(fill="both", expand=True)
        self.bw_list.bind("<<ListboxSelect>>", self.on_bw_select)

        # Right: preview
        preview_frame = ttk.LabelFrame(right, text="Page preview", padding=8)
        preview_frame.pack(fill="both", expand=True)

        self.preview_info = tk.StringVar(value="Select a page from the lists")
        ttk.Label(preview_frame, textvariable=self.preview_info).pack(anchor="w", pady=(0, 8))

        self.preview_label = ttk.Label(preview_frame, anchor="center")
        self.preview_label.pack(fill="both", expand=True)
        self.preview_label.bind("<Configure>", self._on_preview_resize)

    def open_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not path:
            return
        self.pdf_path = Path(path)
        self.file_var.set(str(self.pdf_path))
        self.reset_results()

    def reset_results(self):
        self.total_pages = 0
        self.color_pages = []
        self.bw_pages = []
        self.color_list.delete(0, tk.END)
        self.bw_list.delete(0, tk.END)
        self.stats_var.set("Total: 0   Color: 0   B/W: 0")
        self.color_csv_var.set("")
        self.bw_csv_var.set("")
        self.preview_info.set("Select a page from the lists")
        self.preview_label.configure(image="")
        self._preview_photo = None
        self._preview_pil = None
        self._current_page_num = None
        self._current_category = ""

    def analyze(self):
        if self.pdf_path is None:
            messagebox.showwarning("No file", "Please select a PDF first.")
            return
        if not self.pdf_path.exists():
            messagebox.showerror("Error", f"File not found:\n{self.pdf_path}")
            return

        try:
            total, color = find_color_pages(
                self.pdf_path,
                dpi=self.dpi_var.get(),
                tolerance=self.tolerance_var.get(),
                min_color_ratio=self.min_ratio_var.get(),
                verbose=False,
            )
        except Exception as e:
            messagebox.showerror("Analysis error", str(e))
            return

        color_set = set(color)
        bw = [p for p in range(1, total + 1) if p not in color_set]

        self.total_pages = total
        self.color_pages = color
        self.bw_pages = bw

        self.color_list.delete(0, tk.END)
        self.bw_list.delete(0, tk.END)

        for p in self.color_pages:
            self.color_list.insert(tk.END, str(p))
        for p in self.bw_pages:
            self.bw_list.insert(tk.END, str(p))

        self.stats_var.set(f"Total: {self.total_pages}   Color: {len(self.color_pages)}   B/W: {len(self.bw_pages)}")
        self.color_csv_var.set(",".join(map(str, self.color_pages)))
        self.bw_csv_var.set(",".join(map(str, self.bw_pages)))
        self.preview_info.set("Analysis complete. Select a page to preview.")

    def on_color_select(self, _event):
        idx = self.color_list.curselection()
        if not idx:
            return
        page_num = int(self.color_list.get(idx[0]))
        self._show_preview(page_num, "COLOR")

    def on_bw_select(self, _event):
        idx = self.bw_list.curselection()
        if not idx:
            return
        page_num = int(self.bw_list.get(idx[0]))
        self._show_preview(page_num, "B/W")

    def _show_preview(self, page_num: int, category: str):
        if self.pdf_path is None:
            return
        try:
            doc = pdfium.PdfDocument(str(self.pdf_path))
            page = doc[page_num - 1]
            bitmap = page.render(scale=160 / 72.0)  # render once at decent quality
            self._preview_pil = bitmap.to_pil().convert("RGB")
            self._current_page_num = page_num
            self._current_category = category
            self._update_preview_image()
        except Exception as e:
            messagebox.showerror("Preview error", str(e))

    def _on_preview_resize(self, _event):
        if self._preview_pil is not None:
            self._update_preview_image()

    def _update_preview_image(self):
        if self._preview_pil is None:
            return

        w = max(50, self.preview_label.winfo_width() - 10)
        h = max(50, self.preview_label.winfo_height() - 10)

        img = self._preview_pil.copy()
        img.thumbnail((w, h), Image.Resampling.LANCZOS)

        self._preview_photo = ImageTk.PhotoImage(img)
        self.preview_label.configure(image=self._preview_photo)

        if self._current_page_num is not None:
            self.preview_info.set(f"Page {self._current_page_num} ({self._current_category})")

    def export_split_pdfs(self):
        if self.pdf_path is None or self.total_pages == 0:
            messagebox.showwarning("No analysis", "Analyze a PDF first.")
            return

        color_out = filedialog.asksaveasfilename(
            title="Save color-only PDF as...",
            defaultextension=".pdf",
            initialfile=(self.pdf_path.stem + "_color.pdf"),
            filetypes=[("PDF files", "*.pdf")]
        )
        if not color_out:
            return

        bw_out = filedialog.asksaveasfilename(
            title="Save B/W-only PDF as...",
            defaultextension=".pdf",
            initialfile=(self.pdf_path.stem + "_bw.pdf"),
            filetypes=[("PDF files", "*.pdf")]
        )
        if not bw_out:
            return

        try:
            write_split_pdfs(
                input_pdf=self.pdf_path,
                total_pages=self.total_pages,
                color_pages=self.color_pages,
                out_color_pdf=Path(color_out),
                out_bw_pdf=Path(bw_out),
            )
            messagebox.showinfo("Done", "Split PDFs written successfully.")
        except Exception as e:
            messagebox.showerror("Export error", str(e))


    def copy_color_csv(self):
        self._copy_to_clipboard(self.color_csv_var.get(), "Color page list copied.")

    def copy_bw_csv(self):
        self._copy_to_clipboard(self.bw_csv_var.get(), "B/W page list copied.")

    def _copy_to_clipboard(self, text: str, ok_message: str):
        if not text:
            messagebox.showwarning("Nothing to copy", "The list is empty.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_idletasks()
        messagebox.showinfo("Copied", ok_message)


if __name__ == "__main__":
    app = PdfColorBwGui()
    app.mainloop()