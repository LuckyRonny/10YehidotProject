"""
Convert uml_class_diagrams.html to PDF using Playwright.

Requires: pip install playwright && playwright install chromium

Usage (from project root):
    python html_to_pdf.py
    python html_to_pdf.py path/to/file.html
"""

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Load HTML in headless Chromium, wait for Mermaid to render, export PDF."""
    parser = argparse.ArgumentParser(description="Convert HTML (with Mermaid) to PDF")
    parser.add_argument(
        "html_file",
        nargs="?",
        default=Path(__file__).resolve().parent / "uml_class_diagrams.html",
        type=Path,
        help="Input HTML file (default: uml_class_diagrams.html)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output PDF path (default: same name as HTML with .pdf)",
    )
    args = parser.parse_args()

    html_path = args.html_file.resolve()
    if not html_path.is_file():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    out_path = args.output or html_path.with_suffix(".pdf")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright is required. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    file_url = html_path.as_uri()
    print(f"Opening: {file_url}")
    print(f"Output PDF: {out_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_url, wait_until="networkidle")
        # Wait for Mermaid to render (SVG inside .mermaid containers)
        page.wait_for_selector(".mermaid svg", timeout=15000)
        page.emulate_media(media="print")
        page.pdf(path=str(out_path), format="A4", margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    print(f"Done: {out_path}")


if __name__ == "__main__":
    main()
