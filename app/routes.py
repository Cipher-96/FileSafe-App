import os
import tempfile
from flask import Flask, Response, jsonify, render_template, request, send_file

from app.conversion import convert_file
from app.utils import FILESIZE_LIMIT, is_allowed_extension, is_valid_conversion, make_temp_file_path, normalize_ext, safe_name

PAGES = {
    "home": {"title": "FileSafe | Privacy-first document conversion", "meta_description": "Convert Word, PDF, Excel, PowerPoint, JPG and more without login or tracking."},
    "about": {"title": "About FileSafe", "meta_description": "Learn how FileSafe keeps conversion secure and private."},
    "privacy": {"title": "Privacy Policy", "meta_description": "No login, no tracking, no personal data collection."},
    "terms": {"title": "Terms of Service", "meta_description": "Terms for using FileSafe."},
    "contact": {"title": "Contact FileSafe", "meta_description": "Contact us with questions or feedback."},
    "faq": {"title": "FAQ | FileSafe", "meta_description": "Frequently asked questions about FileSafe."}
}


def register_routes(app: Flask):
    @app.route("/")
    def index():
        return render_template("index.html", page=PAGES["home"])

    @app.route("/robots.txt")
    def robots():
        return Response("User-agent: *\nAllow: /\nSitemap: https://filesafe.eu/sitemap.xml\n", mimetype="text/plain")

    @app.route("/sitemap.xml")
    def sitemap():
        urls = [
            "https://filesafe.eu/",
            "https://filesafe.eu/about",
            "https://filesafe.eu/privacy-policy",
            "https://filesafe.eu/terms-of-service",
            "https://filesafe.eu/contact",
            "https://filesafe.eu/faq",
            "https://filesafe.eu/docx-to-pdf",
            "https://filesafe.eu/pptx-to-pdf",
            "https://filesafe.eu/xlsx-to-pdf",
            "https://filesafe.eu/pdf-to-word",
            "https://filesafe.eu/pdf-to-powerpoint",
            "https://filesafe.eu/pdf-to-excel",
            "https://filesafe.eu/jpg-to-pdf",
            "https://filesafe.eu/pdf-to-jpg",
        ]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for url in urls:
            xml += f"  <url><loc>{url}</loc></url>\n"
        xml += "</urlset>\n"
        return Response(xml, mimetype="application/xml")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/convert", methods=["POST"])
    def convert_upload():
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        uploaded = request.files["file"]
        if uploaded.filename == "":
            return jsonify({"error": "No file selected"}), 400

        source = normalize_ext(request.form.get("source", ""))
        target = normalize_ext(request.form.get("target", ""))
        if not source or not target:
            return jsonify({"error": "Missing conversion source/target"}), 400
        if not is_valid_conversion(source, target):
            return jsonify({"error": "Unsupported conversion pair"}), 400

        filename = safe_name(uploaded.filename)
        ext = os.path.splitext(filename)[1].lstrip(".")
        if not is_allowed_extension(ext):
            return jsonify({"error": "Unsupported file type"}), 400

        temp_dir = tempfile.mkdtemp(prefix="filesafe-", dir="tmp")
        temp_input = make_temp_file_path(temp_dir, filename)
        uploaded.save(temp_input)

        if os.path.getsize(temp_input) > FILESIZE_LIMIT:
            return jsonify({"error": "File exceeds 100 MB file size limit"}), 400

        try:
            output_path = convert_file(temp_input, source, target, temp_dir)
            if not os.path.exists(output_path):
                return jsonify({"error": "Conversion failed"}), 500
            response = send_file(output_path, as_attachment=True, download_name=os.path.basename(output_path))

            def cleanup():
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for item in files:
                        try:
                            os.remove(os.path.join(root, item))
                        except OSError:
                            pass
                    for item in dirs:
                        try:
                            os.rmdir(os.path.join(root, item))
                        except OSError:
                            pass
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass

            response.call_on_close(cleanup)
            return response
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/docx-to-pdf")
    def docx_to_pdf():
        return render_template("convert.html", page=PAGES["home"], title="DOCX to PDF", heading="Convert DOCX to PDF", intro="Upload a DOCX file and convert it to PDF securely.", source="docx", target="pdf")

    @app.route("/pptx-to-pdf")
    def pptx_to_pdf():
        return render_template("convert.html", page=PAGES["home"], title="PPTX to PDF", heading="Convert PPTX to PDF", intro="Turn a presentation into an easy-to-share PDF.", source="pptx", target="pdf")

    @app.route("/xlsx-to-pdf")
    def xlsx_to_pdf():
        return render_template("convert.html", page=PAGES["home"], title="XLSX to PDF", heading="Convert XLSX to PDF", intro="Turn your spreadsheet into a PDF file.", source="xlsx", target="pdf")

    @app.route("/pdf-to-word")
    def pdf_to_word():
        return render_template("convert.html", page=PAGES["home"], title="PDF to Word", heading="Convert PDF to Word", intro="Convert your PDF into DOCX or DOC.", source="pdf", target="docx")

    @app.route("/pdf-to-powerpoint")
    def pdf_to_powerpoint():
        return render_template("convert.html", page=PAGES["home"], title="PDF to PowerPoint", heading="Convert PDF to PowerPoint", intro="Turn a PDF into a PowerPoint presentation.", source="pdf", target="pptx")

    @app.route("/pdf-to-excel")
    def pdf_to_excel():
        return render_template("convert.html", page=PAGES["home"], title="PDF to Excel", heading="Convert PDF to Excel", intro="Export PDF content to Excel.", source="pdf", target="xlsx")

    @app.route("/jpg-to-pdf")
    def jpg_to_pdf():
        return render_template("convert.html", page=PAGES["home"], title="JPG to PDF", heading="Convert JPG to PDF", intro="Convert images into a PDF document.", source="jpg", target="pdf")

    @app.route("/pdf-to-jpg")
    def pdf_to_jpg():
        return render_template("convert.html", page=PAGES["home"], title="PDF to JPG", heading="Convert PDF to JPG", intro="Convert each page to JPG or PNG.", source="pdf", target="jpg")

    @app.route("/about")
    def about():
        return render_template("static_page.html", page=PAGES["about"], title="About FileSafe")

    @app.route("/privacy-policy")
    def privacy_policy():
        return render_template("static_page.html", page=PAGES["privacy"], title="Privacy Policy")

    @app.route("/terms-of-service")
    def terms_of_service():
        return render_template("static_page.html", page=PAGES["terms"], title="Terms of Service")

    @app.route("/contact")
    def contact():
        return render_template("static_page.html", page=PAGES["contact"], title="Contact")

    @app.route("/faq")
    def faq():
        return render_template("static_page.html", page=PAGES["faq"], title="FAQ")

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404
