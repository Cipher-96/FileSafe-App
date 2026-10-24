import os
import shutil
import subprocess

from PIL import Image
from pypdf import PdfReader
from weasyprint import HTML

from app.utils import ensure_secure_temp_dir, is_valid_conversion


def libreoffice_convert(input_path: str, target_format: str, out_dir: str) -> str:
    output_dir = ensure_secure_temp_dir(out_dir)
    cmd = [
        "libreoffice",
        "--headless",
        "--nologo",
        "--nodefault",
        "--convert-to",
        target_format,
        "--outdir",
        output_dir,
        input_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    source_name = os.path.splitext(os.path.basename(input_path))[0]
    candidate = os.path.join(output_dir, f"{source_name}.{target_format}")
    if os.path.exists(candidate):
        return candidate
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.lower().endswith(f".{target_format.lower()}"):
                return os.path.join(root, file)
    raise FileNotFoundError(f"Conversion output for {target_format} not found")


def image_to_pdf(input_path: str, out_dir: str) -> str:
    output = os.path.join(out_dir, "converted.pdf")
    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")
        img.save(output, "PDF", resolution=100.0)
    return output


def pdf_to_images(input_path: str, target_ext: str, out_dir: str) -> str:
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm is not installed")
    prefix = os.path.join(out_dir, "converted")
    cmd = ["pdftoppm", "-png" if target_ext.lower() == "png" else "-jpeg", "-r", "200", input_path, prefix]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for root, _, files in os.walk(out_dir):
        for file in files:
            if file.lower().endswith(f".{target_ext.lower()}"):
                return os.path.join(root, file)
    raise FileNotFoundError(f"Image conversion not found in {out_dir}")


def html_to_pdf(input_path: str, out_dir: str) -> str:
    output = os.path.join(out_dir, "converted.pdf")
    HTML(filename=input_path).write_pdf(output)
    return output


def pdf_to_html(input_path: str, out_dir: str) -> str:
    output = os.path.join(out_dir, "converted.html")
    reader = PdfReader(input_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    html = "<html><body>" + "".join(f"<p>{p}</p>" for p in pages) + "</body></html>"
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    return output


def convert_file(input_path: str, source_ext: str, target_ext: str, out_dir: str) -> str:
    source = source_ext.lower().lstrip(".")
    target = target_ext.lower().lstrip(".")

    if source in {"doc", "docx", "ppt", "pptx", "xls", "xlsx"} and target == "pdf":
        return libreoffice_convert(input_path, "pdf", out_dir)
    if source == "pdf" and target in {"doc", "docx", "ppt", "pptx", "xls", "xlsx"}:
        return libreoffice_convert(input_path, target, out_dir)
    if source in {"jpg", "jpeg", "png"} and target == "pdf":
        return image_to_pdf(input_path, out_dir)
    if source == "pdf" and target in {"jpg", "png"}:
        return pdf_to_images(input_path, target, out_dir)
    if source == "html" and target == "pdf":
        return html_to_pdf(input_path, out_dir)
    if source == "pdf" and target == "html":
        return pdf_to_html(input_path, out_dir)

    raise ValueError(f"Unsupported conversion: {source} -> {target}")
