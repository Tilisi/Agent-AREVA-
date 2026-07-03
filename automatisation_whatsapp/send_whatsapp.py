import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / "config" / ".env"
if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)

logger = logging.getLogger(__name__)


class WhatsAppClient:
    def __init__(self, token: Optional[str] = None, phone_number_id: Optional[str] = None):
        self.token = token or os.getenv("WHATSAPP_TOKEN", "")
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def _format_phone(self, phone: str) -> str:
        clean = ''.join(filter(str.isdigit, phone))
        if clean.startswith("00216"):
            return clean[2:]
        if clean.startswith("0"):
            return "216" + clean[1:]
        if len(clean) == 8:
            return "216" + clean
        return clean

    async def send_text_message(self, recipient_phone: str, message_text: str) -> Dict[str, Any]:
        if not self.token or self.token.startswith("VOTRE_") or not self.phone_number_id:
            logger.warning("WhatsApp API credentials non configurées. Envoi simulé.")
            return {"status": "simulated", "recipient": recipient_phone, "text": message_text}

        formatted_phone = self._format_phone(recipient_phone)
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "text",
            "text": {"preview_url": False, "body": message_text}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                logger.error(f"Erreur HTTP lors de l'envoi WhatsApp vers {formatted_phone} : {exc}")
                return {"error": str(exc), "status": "failed"}

    async def send_order_confirmation(self, recipient_phone: str, nom: str, ref_commande: str, montant_tnd: float) -> Dict[str, Any]:
        if not self.token or self.token.startswith("VOTRE_") or not self.phone_number_id:
            logger.warning("WhatsApp API credentials non configurées. Envoi simulé.")
            return {"status": "simulated", "recipient": recipient_phone, "ref": ref_commande}

        formatted_phone = self._format_phone(recipient_phone)
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Envoi prioritaire par Template officiel approuvé par Meta (contourne la règle des 24h)
        payload_template = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": "arvea_order_confirm",
                "language": {"code": "ar"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": nom},
                            {"type": "text", "text": ref_commande},
                            {"type": "text", "text": f"{montant_tnd:.2f} TND"}
                        ]
                    }
                ]
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, json=payload_template, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Template échoué ({response.status_code}). Tentative Fallback Texte libre...")
            except Exception as exc:
                logger.warning(f"Exception Template WhatsApp : {exc}. Tentative Fallback...")

            # Fallback Draconien : Texte libre en cas d'interaction < 24h
            text_recap = (
                f"مرحبا {nom} 🌿\n"
                f"تم تأكيد طلبك بنجاح من أرفيا العناية الطبيعية (Arvea Nature)!\n"
                f"📦 مرجع الطلب: {ref_commande}\n"
                f"💰 المبلغ الإجمالي: {montant_tnd:.2f} دينار تونسي (TND)\n"
                f"🚚 التوصيل خلال 24 إلى 48 ساعة لكامل تراب الجمهورية.\n"
                f"شكراً لثقتكم بنا! للتواصل المباشر نحن في خدمتكم."
            )
            return await self.send_text_message(recipient_phone, text_recap)
