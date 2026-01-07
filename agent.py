import os
import feedparser
import smtplib
import logging
import time
from google import genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración 2026 para Gemini 2.5 Flash Lite 
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1'})
MODEL_ID = "gemini-2.5-flash-lite" 

HISTORY_FILE = "processed_ids.txt"

def get_processed_ids():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f:
        return f.read().splitlines()

def save_processed_ids(ids):
    with open(HISTORY_FILE, "a") as f:
        for entry_id in ids:
            f.write(entry_id + "\n")

def analyze_with_priority(news_list):
    content_to_analyze = ""
    for i, news in enumerate(news_list, 1):
        content_to_analyze += f"ID:{i} | Título: {news['title']} | Resumen: {news['summary']} | Fuente: {news['source']} | Link: {news['link']}\n\n"

    prompt = f"""
    Eres un Analista de Ciberinteligencia Senior. Tu misión es organizar este reporte para que sea ALTAMENTE LEGIBLE.
    
    ORDEN DE PRIORIDAD:
    1. Banca, Fintech, Inversión y Startups.
    2. Filtraciones de datos, Fuerza Bruta y Ataques de Numeración.
    3. Resto de sectores.

    FORMATO HTML REQUERIDO (Sigue esto estrictamente):
    Para cada noticia, crea una tarjeta con este estilo:
    <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 25px; background-color: #f9f9f9;">
        <h2 style="color: #2c3e50; margin-top: 0;">[Título de la Noticia]</h2>
        
        <div style="margin-bottom: 10px;">
            <span style="background-color: [COLOR_FONDO]; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px;">
                CRITICIDAD: [VALOR ORIGINAL]
            </span>
            <span style="margin-left: 10px; color: #7f8c8d; font-size: 12px;">Fuente: [Nombre de la Fuente]</span>
        </div>

        <p><b>1. DESCRIPCIÓN:</b> [Resumen técnico detallado]</p>
        <p><b>2. RECOMENDACIÓN:</b> [Acción inmediata sugerida]</p>
        <p><b>3. INDICADORES DE COMPROMISO (IoCs):</b> <code style="background: #eee; padding: 2px 5px;">[Lista técnica]</code></p>
        
        <div style="margin-top: 15px;">
            <a href="[LINK]" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Ver fuente oficial →</a>
        </div>
    </div>

    COLORES DE CRITICIDAD:
    - Crítica: #c0392b (Rojo)
    - Alta: #e67e22 (Naranja)
    - Media/Baja: #27ae60 (Verde)

    NOTICIAS:
    {content_to_analyze}
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            return response.text
        except Exception as e:
            if "503" in str(e) or "overloaded" in str(e):
                wait_time = (attempt + 1) * 30  # Espera 30s, luego 60s...
                logging.warning(f"Servidor sobrecargado. Reintento {attempt+1}/{max_retries} en {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Error no recuperable en IA: {e}")
                break
    return None

def send_email(body_html):
    msg = MIMEMultipart()
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = os.getenv("EMAIL_RECEIVER")
    msg['Subject'] = f"🛡️ INTEL REPORT: {time.strftime('%d/%m/%Y')}"

    # Envolvemos todo el contenido en un contenedor principal para centrarlo
    full_html = f"""
    <html>
        <body style="background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h1 style="text-align: center; color: #2c3e50;">Resumen Diario de Inteligencia</h1>
                <p style="text-align: center; color: #7f8c8d;">Prioridad: Sector Financiero y Amenazas de Datos</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                {body_html}
                <footer style="text-align: center; font-size: 12px; color: #bdc3c7; margin-top: 30px;">
                    Agente de Ciberseguridad Gemini v2026 - Generado automáticamente
                </footer>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(full_html, 'html'))
    
    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)
            logging.info("✅ Reporte enviado con éxito.")
    except Exception as e:
        logging.error(f"❌ Error al enviar correo: {e}")

def run_agent():
    logging.info("--- 🕵️ Iniciando Agente de Inteligencia ---")
    rss_sources = os.getenv("RSS_URLS").split(",")
    processed_ids = get_processed_ids()
    
    all_new_entries = []
    
    for url in rss_sources:
        feed = feedparser.parse(url.strip())
        source_name = feed.feed.get('title', 'Fuente desconocida')
        
        # Recogemos todas las noticias nuevas (sin límite de 3)
        for entry in feed.entries:
            if entry.link not in processed_ids:
                all_new_entries.append({
                    'title': entry.title,
                    'summary': entry.summary,
                    'link': entry.link,
                    'source': source_name
                })

    if all_new_entries:
        logging.info(f"Analizando {len(all_new_entries)} noticias encontradas hoy...")
        # Enviamos todas a la IA para que ella filtre y ordene
        report_html = analyze_with_priority(all_new_entries)
        
        if report_html:
            send_email(report_html)
            save_processed_ids([n['link'] for n in all_new_entries])
    else:
        logging.info("No hay noticias nuevas desde la última ejecución.")

if __name__ == "__main__":
    run_agent()