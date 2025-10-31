# handlers.py
from pdf_generator import generate_cv_pdf

def handle_download_cv(user_id):
    try:
        pdf_bytes = generate_cv_pdf(user_id)
        return {'success': True, 'pdf_bytes': pdf_bytes}
    except Exception as e:
        return {'success': False, 'error': str(e)}
