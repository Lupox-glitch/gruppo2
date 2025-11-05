import logging
import re
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, FrameBreak
)
from database import get_db_connection

# === LOGGER CONFIG ===
logger = logging.getLogger(__name__)

# === SANITIZATION ===
def sanitize_input(text):
    """Rimuove tag o caratteri potenzialmente pericolosi mantenendo la formattazione base."""
    if not text:
        return ""
    cleaned = str(text)
    cleaned = cleaned.replace('<', '&lt;').replace('>', '&gt;')
    cleaned = re.sub(r'[\x00-\x1f\x7f]', '', cleaned)  # rimuove caratteri di controllo invisibili
    return cleaned.strip()


# === DB FETCH ===
def _fetch_user_full(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    cur.execute("SELECT * FROM cv_data WHERE user_id=%s", (user_id,))
    cv = cur.fetchone() or {}

    cur.execute("SELECT * FROM experiences WHERE user_id=%s ORDER BY data_inizio DESC", (user_id,))
    experiences = cur.fetchall() or []

    conn.close()
    return user, cv, experiences


# === CALLBACK per disegnare sfondo colonna sinistra ===
def draw_background(canvas, doc):
    """Disegna lo sfondo grigio nella colonna sinistra."""
    canvas.saveState()
    left_x = doc.leftMargin
    left_y = doc.bottomMargin
    left_width = 6 * cm
    left_height = A4[1] - doc.topMargin - doc.bottomMargin
    canvas.setFillColor(colors.HexColor('#F5F5F5'))
    canvas.rect(left_x, left_y, left_width, left_height, fill=True, stroke=False)
    canvas.restoreState()

# === Competenze e lingue ===
def add_text_or_list(story, title, text, styles):
    story.append(Paragraph(title, styles['SectionTitle']))
    if not text:
        story.append(Paragraph("Nessun dato inserito", styles['Body']))
        return
    if ',' in text:
        for item in [t.strip() for t in text.split(',') if t.strip()]:
            story.append(Paragraph(f"• {sanitize_input(item)}", styles['Body']))
    else:
        story.append(Paragraph(sanitize_input(text), styles['Body']))
    story.append(Spacer(1, 10))


# === PDF GENERATOR ===
def generate_cv_pdf(user_id):
    """Genera un CV in layout a due colonne e restituisce i bytes del PDF."""
    try:
        if not isinstance(user_id, int):
            raise ValueError(f"user_id non valido: {user_id}")

        user, cv, experiences = _fetch_user_full(user_id)
        if not user:
            raise ValueError(f"Utente non trovato (user_id={user_id})")

        buffer = BytesIO()

        # === Layout ===
        width, height = A4
        margin = 1.5 * cm
        left_width = 6 * cm
        gap = 0.5 * cm
        right_width = width - left_width - gap - (2 * margin)

        # Frame sinistro e destro
        left_frame = Frame(
            margin, margin, left_width, height - 2 * margin,
            leftPadding=10, rightPadding=10, topPadding=10, bottomPadding=10, id='left'
        )
        right_frame = Frame(
            margin + left_width + gap, margin, right_width, height - 2 * margin,
            leftPadding=10, rightPadding=10, topPadding=10, bottomPadding=10, id='right'
        )

        # === Stili ===
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Header', fontSize=26, textColor=colors.HexColor('#2E86AB'),
                                  alignment=1, leading=30, spaceAfter=12))
        styles.add(ParagraphStyle(name='SectionTitle', fontSize=13, textColor=colors.HexColor('#2E86AB'),
                                  spaceBefore=10, spaceAfter=6, leading=14))
        styles.add(ParagraphStyle(name='Body', fontSize=10.5, textColor=colors.HexColor('#333333'), leading=13))
        styles.add(ParagraphStyle(name='Small', fontSize=9, textColor=colors.gray, alignment=1))

        # === Documento con due frame ===
        doc = BaseDocTemplate(buffer, pagesize=A4,
                              leftMargin=margin, rightMargin=margin,
                              topMargin=margin, bottomMargin=margin)
        template = PageTemplate(id='TwoCol', frames=[left_frame, right_frame], onPage=draw_background)
        doc.addPageTemplates([template])

        story = []

        # === HEADER ===
        full_name = f"{sanitize_input(user.get('nome'))} {sanitize_input(user.get('cognome'))}".strip()
        story.append(Paragraph(full_name or "Utente Sconosciuto", styles['Header']))
        story.append(Spacer(1, 8))

        # === COLONNA SINISTRA ===
        left_story = []

        # Contatti
        left_story.append(Paragraph("Contatti", styles['SectionTitle']))
        contact_lines = []

        phone = cv.get('telefono')
        if phone and phone.strip():
            contact_lines.append(f"{sanitize_input(phone)}")

        email = user.get('email')
        if email and email.strip():
            contact_lines.append(f"{sanitize_input(email)}")

        linkedin = cv.get('linkedin_url')
        if linkedin and linkedin.strip():
            contact_lines.append(f"{sanitize_input(linkedin)}")

        city = cv.get('citta')
        if city and city.strip():
            contact_lines.append(f"{sanitize_input(city)}")

        for line in contact_lines:
            left_story.append(Paragraph(line, styles['Body']))

        left_story.append(Spacer(1, 10))

        # Competenze
        add_text_or_list(left_story, "Competenze", cv.get('skills', ''), styles)

        # Lingue
        add_text_or_list(left_story, "Lingue", cv.get('languages', ''), styles)

        # === COLONNA DESTRA ===
        right_story = []

        # Esperienze lavorative
        work = [e for e in experiences if e['tipo'] == 'lavoro']
        if work:
            right_story.append(Paragraph("Esperienze Lavorative", styles['SectionTitle']))
            for e in work:
                periodo = f"{e['data_inizio']} - {'In corso' if e['is_current'] else (e.get('data_fine') or '')}"
                titolo = sanitize_input(e.get('titolo'))
                azienda = sanitize_input(e.get('azienda_istituto'))
                right_story.append(Paragraph(f"<b>{titolo}</b> — {azienda}", styles['Body']))
                right_story.append(Paragraph(periodo, styles['Body']))
                if e.get('descrizione'):
                    right_story.append(Paragraph(sanitize_input(e['descrizione']), styles['Body']))
                right_story.append(Spacer(1, 6))

        # Formazione
        edu = [e for e in experiences if e['tipo'] == 'formazione']
        if edu:
            right_story.append(Spacer(1, 6))
            right_story.append(Paragraph("Formazione", styles['SectionTitle']))
            for e in edu:
                periodo = f"{e['data_inizio']} - {'In corso' if e['is_current'] else (e.get('data_fine') or '')}"
                titolo = sanitize_input(e.get('titolo'))
                istituto = sanitize_input(e.get('azienda_istituto'))
                right_story.append(Paragraph(f"<b>{titolo}</b> — {istituto}", styles['Body']))
                right_story.append(Paragraph(periodo, styles['Body']))
                if e.get('descrizione'):
                    right_story.append(Paragraph(sanitize_input(e['descrizione']), styles['Body']))
                right_story.append(Spacer(1, 6))

        # Footer
        right_story.append(Spacer(1, 12))
        right_story.append(Paragraph(f"Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Small']))

        # === Combina ===
        story.extend(left_story)
        story.append(FrameBreak())  # passa alla colonna destra
        story.extend(right_story)

        # === Build PDF ===
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    except Exception as e:
        logger.exception(f"Errore generazione PDF per user {user_id}: {e}")
        raise
