# 🕵️ AI Cyber-Intelligence Agent (Financial Sector Priority)

Este es un agente de ciberseguridad autónomo diseñado para monitorear feeds RSS de fuentes globales (como CISA y The Hacker News), analizar las amenazas mediante **Google Gemini AI (v2026)** y generar reportes visuales consolidados por correo electrónico.

## 🚀 Características Principales

* **Priorización Inteligente**: El motor de IA organiza las noticias dando prioridad al **Sector Financiero, Banca, Fintech e Inversión**.
* **Detección de Amenazas Críticas**: Foco especial en ataques de fuerza bruta, enumeración y filtraciones de bases de datos.
* **Análisis Consolidado**: Agrupa múltiples noticias en un único reporte tipo "Dashboard" para optimizar la cuota de la API y mejorar la lectura.
* **Reportes Visuales**: Correos electrónicos en formato HTML con código de colores para criticidad (Semáforo).
* **Automatización Linux**: Configurado para ejecutarse diariamente vía `cron`.

## 🛠️ Stack Tecnológico

* **Python 3.10+**
* **Google GenAI SDK**: Integración con Gemini 2.5/3 Flash.
* **Feedparser**: Procesamiento de fuentes RSS.
* **SMTPLib**: Envío de reportes automatizados.

## 📋 Requisitos Obligatorios en Reportes

Cada análisis generado por el agente incluye:
1.  **Descripción**: Resumen técnico fiel a la fuente.
2.  **Criticidad**: Nivel de severidad original (Crítica/Alta/Media/Baja).
3.  **Recomendaciones**: Acciones inmediatas sugeridas por la IA.
4.  **IoCs**: Indicadores de Compromiso (IPs, Hashes, Dominios).

## ⚙️ Instalación y Configuración

1. **Clonar y preparar entorno**:
   ```bash
   git clone https://github.com/cdanielrua/cyberintelligence_agent.git
   cd cyber-agent
   python3 -m venv venv
   source venv/bin/activate
   pip install google-genai feedparser python-dotenv
   ```

2. **Variables de Entorno: Crea un archivo .env con las siguientes credenciales**:

```Fragmento de código

GEMINI_API_KEY=tu_key_aqui
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASSWORD=tu_app_password
EMAIL_RECEIVER=correo_destino@gmail.com
RSS_URLS=[https://www.cisa.gov/cybersecurity-advisories/all.xml](https://www.cisa.gov/cybersecurity-advisories/all.xml), [https://feeds.feedburner.com/TheHackersNews](https://feeds.feedburner.com/TheHackersNews)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```
## 🤖 Automatización
El agente está diseñado para ejecutarse mediante un script lanzador run_agent.sh programado en el crontab de Linux para reportes diarios.
