import os
import smtplib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / "config" / ".env"
if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="GmailWorker")


class GmailSender:
    def __init__(self, sender_email: Optional[str] = None, app_password: Optional[str] = None):
        self.sender_email = sender_email or os.getenv("GMAIL_SENDER_EMAIL", "")
        self.app_password = app_password or os.getenv("GMAIL_APP_PASSWORD", "")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465

    def send_email(self, recipient_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        if not self.sender_email or not self.app_password or "votre_" in self.sender_email:
            logger.warning(f"Identifiants Gmail non configurés. Notification simulée pour : {recipient_email}")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"Arvea Nature Automations <{self.sender_email}>"
        message["To"] = recipient_email

        if text_content:
            part1 = MIMEText(text_content, "plain", "utf-8")
            message.attach(part1)

        part2 = MIMEText(html_content, "html", "utf-8")
        message.attach(part2)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=5.0) as server:
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            logger.info(f"Email envoyé avec succès à {recipient_email}")
            return True
        except Exception as exc:
            logger.error(f"Erreur lors de l'envoi de l'email via Gmail SMTP SSL : {exc}")
            return False

    async def send_email_async(self, recipient_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(_executor, self.send_email, recipient_email, subject, html_content, text_content),
                timeout=7.0
            )
        except asyncio.TimeoutError:
            logger.error(f"Abandon draconien : Timeout réseau (>7s) lors de l'envoi email vers {recipient_email}")
            return False

    def send_kpi_report(self, recipient_email: str, stats: Dict[str, Any]) -> bool:
        subject = "📊 Rapport Journalier des KPI - Arvea Nature Tunisie"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="background-color: #1a5e3a; color: white; padding: 20px; text-align: center; border-radius: 5px;">
                <h1>Arvea Nature - Dashboard Automatisé</h1>
            </div>
            <div style="padding: 20px;">
                <h2>Résumé des Performances</h2>
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Indicateur</th>
                        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Valeur</th>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Total Prospects</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{stats.get('total_prospects', 0)}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Commandes Confirmées</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{stats.get('total_commandes', 0)}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Chiffre d'Affaires Généré</td>
                        <td style="padding: 12px; border: 1px solid #ddd; color: #1a5e3a;"><strong>{stats.get('chiffre_affaires_tnd', 0.0)} TND</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Taux de Conversion</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{stats.get('taux_conversion_pct', 0.0)} %</strong></td>
                    </tr>
                </table>
                <p style="margin-top: 20px; font-size: 12px; color: #777;">
                    Généré automatiquement sur appareil Android (Termux) via le moteur d'orchestration Arvea.
                </p>
            </div>
        </body>
        </html>
        """
        return self.send_email(recipient_email, subject, html)
