# FileSafe

A privacy-first document conversion website with no login, no tracking, and temporary file cleanup.

## Features
- DOC, DOCX, PPT, PPTX, XLS, XLSX, PDF, JPG, PNG, HTML conversion support
- Drag-and-drop uploads
- 100 MB file limit
- Secure temp-file workflow
- No login, tracking, or personal data collection
- Responsive landing pages and legal pages

## Local setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt-get update
sudo apt-get install -y libreoffice poppler-utils libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev
python app.py
```

Open: http://localhost:5000

## Production
Use gunicorn:
```bash
gunicorn app:app
```

## Notes
- LibreOffice is required for DOC/PPT/XLS conversions.
- Poppler is required for PDF image conversions.
