elif path == '/api/download-pdf':
    if not session.get('user_id'):
        self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
        return

    from handlers import handle_download_cv
    result = handle_download_cv(session['user_id'])

    if not result['success']:
        self._send_json(result, 500)
        return

    self.send_response(200)
    self.send_header('Content-Type', 'application/pdf')
    self.send_header('Content-Disposition', f'attachment; filename="cv_{session["user_id"]}.pdf"')
    self.end_headers()
    self.wfile.write(result['pdf_bytes'])