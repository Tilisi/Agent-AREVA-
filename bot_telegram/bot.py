import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / "config" / ".env"
if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)

CONFIG_PATH = BASE_DIR / "config" / "config_global.json"
FAQ_PATH = BASE_DIR / "bot_telegram" / "faq.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG_DATA = json.load(f)

with open(FAQ_PATH, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

import sys
sys.path.append(str(BASE_DIR))
from gestion_prospects.prospect_manager import ProspectManager
from automatisation_whatsapp.send_whatsapp import WhatsAppClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

(
    CHOIX_LANGUE,
    MENU_PRINCIPAL,
    MENU_PRODUITS,
    MENU_FAQ,
    SAISIE_QUANTITE,
    SAISIE_NOM,
    SAISIE_TELEPHONE,
    SAISIE_VILLE
) = range(8)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("🇹🇳 تونسي (Derja)", callback_data="lang_ar")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "مرحباً بكم في أرفيا العناية الطبيعية (Arvea Nature) 🌿\n"
        "Bienvenue chez Arvea Nature Tunisie 🌿\n\n"
        "الرجاء اختيار اللغة / Veuillez choisir votre langue :"
    )
    if update.message:
        await update.message.reply_text(msg, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    return CHOIX_LANGUE


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang

    return await afficher_menu_principal(query, context)


async def afficher_menu_principal(query_or_message, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "fr")
    if lang == "ar":
        text = "القائمة الرئيسية 🌿 أرفيا الطبيعة التونسية:\nكيفاش نجمو نعاونوك اليوم؟"
        keyboard = [
            [InlineKeyboardButton("🛍️ تصفح وطلب المنتوجات", callback_data="menu_prod")],
            [InlineKeyboardButton("❓ الأسئلة الشائعة (التوصيل، الدفع...)", callback_data="menu_faq")],
            [InlineKeyboardButton("🌐 تغيير اللغة", callback_data="change_lang")]
        ]
    else:
        text = "Menu Principal 🌿 Arvea Nature Tunisie :\nComment pouvons-nous vous aider aujourd'hui ?"
        keyboard = [
            [InlineKeyboardButton("🛍️ Catalogue et Commander", callback_data="menu_prod")],
            [InlineKeyboardButton("❓ Questions Fréquentes (FAQ)", callback_data="menu_faq")],
            [InlineKeyboardButton("🌐 Changer de langue", callback_data="change_lang")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    if hasattr(query_or_message, "edit_message_text"):
        await query_or_message.edit_message_text(text, reply_markup=reply_markup)
    else:
        await query_or_message.reply_text(text, reply_markup=reply_markup)
    return MENU_PRINCIPAL


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "change_lang":
        return await start(update, context)
    elif choice == "menu_prod":
        return await afficher_produits(query, context)
    elif choice == "menu_faq":
        return await afficher_faq(query, context)
    elif choice == "retour_main":
        return await afficher_menu_principal(query, context)
    return MENU_PRINCIPAL


async def afficher_produits(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "fr")
    keyboard = []
    for prod in CONFIG_DATA["produits"]:
        nom = prod["nom"]
        prix = prod["prix_tnd"]
        btn_text = f"{nom} - {prix:.2f} TND"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_{prod['id']}")])

    if lang == "ar":
        keyboard.append([InlineKeyboardButton("🔙 الرجوع للقائمة الرئيسية", callback_data="retour_main")])
        text = "منتوجات أرفيا الطبيعية المصادق عليها 🌿\nاختر المنتوج لتقديم طلبك :"
    else:
        keyboard.append([InlineKeyboardButton("🔙 Retour au Menu Principal", callback_data="retour_main")])
        text = "Nos Produits Arvea Nature 100% naturels 🌿\nSélectionnez un produit pour commander :"

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)
    return MENU_PRODUITS


async def selectionner_produit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "retour_main":
        return await afficher_menu_principal(query, context)

    prod_id = query.data.split("_")[1]
    selected_prod = next((p for p in CONFIG_DATA["produits"] if p["id"] == f"prod_{prod_id}" or p["id"] == prod_id or prod_id in p["id"]), None)
    if not selected_prod:
        selected_prod = CONFIG_DATA["produits"][0]

    context.user_data["produit_choisi"] = selected_prod
    lang = context.user_data.get("lang", "fr")

    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="qte_1"),
            InlineKeyboardButton("2", callback_data="qte_2"),
            InlineKeyboardButton("3", callback_data="qte_3")
        ]
    ]
    if lang == "ar":
        text = f"لقد اخترت : {selected_prod['nom']} السعر : {selected_prod['prix_tnd']} دينار.\nالرجاء تحديد الكمية المطلوبة :"
    else:
        text = f"Produit sélectionné : {selected_prod['nom']} au prix de {selected_prod['prix_tnd']} TND.\nVeuillez choisir la quantité souhaitée :"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return SAISIE_QUANTITE


async def selectionner_quantite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    qte = int(query.data.split("_")[1])
    context.user_data["quantite"] = qte
    lang = context.user_data.get("lang", "fr")

    if lang == "ar":
        text = "ممتاز! الرجاء كتابة اسمك الكامل (الاسم واللقب) لتسجيل الطلب :"
    else:
        text = "Parfait ! Veuillez écrire votre Nom et Prénom complets :"

    await query.edit_message_text(text)
    return SAISIE_NOM


async def recevoir_nom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["nom_complet"] = update.message.text.strip()
    lang = context.user_data.get("lang", "fr")

    if lang == "ar":
        text = "شكراً! الرجاء كتابة رقم هاتفك (مثال : 20123456) للتواصل معك وتأكيد التوصيل :"
    else:
        text = "Merci ! Veuillez entrer votre numéro de téléphone tunisien (ex: 20123456) :"

    await update.message.reply_text(text)
    return SAISIE_TELEPHONE


async def recevoir_telephone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["telephone"] = update.message.text.strip()
    lang = context.user_data.get("lang", "fr")

    if lang == "ar":
        text = "أخيراً، اكتب الولاية أو المدينة التي تقيم بها (مثال: تونس، صفاقس، سوسة...) :"
    else:
        text = "Enfin, indiquez votre ville ou gouvernorat de livraison (ex: Tunis, Sfax, Sousse...) :"

    await update.message.reply_text(text)
    return SAISIE_VILLE


async def recevoir_ville_et_confirmer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ville = update.message.text.strip()
    context.user_data["ville"] = ville
    lang = context.user_data.get("lang", "fr")

    nom = context.user_data["nom_complet"]
    phone = context.user_data["telephone"]
    prod = context.user_data["produit_choisi"]
    qte = context.user_data["quantite"]

    total_produits = prod["prix_tnd"] * qte
    frais_livraison = 0.0 if total_produits >= CONFIG_DATA["livraison"]["seuil_livraison_gratuite_tnd"] else CONFIG_DATA["livraison"]["frais_standard_tnd"]
    montant_total = total_produits + frais_livraison

    pm = ProspectManager()
    prospect_id = pm.ajouter_ou_mettre_a_jour_prospect(nom, phone, ville, lang, "telegram_bot")

    produits_list = [{"id": prod["id"], "nom": prod["nom"], "quantite": qte, "prix_unitaire_tnd": prod["prix_tnd"]}]
    ref_cmd = pm.creer_commande(prospect_id, json.dumps(produits_list, ensure_ascii=False), montant_total, frais_livraison)

    wa_client = WhatsAppClient()
    await wa_client.send_order_confirmation(phone, nom, ref_cmd, montant_total)

    if lang == "ar":
        recap = (
            f"✅ تم تأكيد طلبك بنجاح في نظام أرفيا التونسي!\n\n"
            f"📦 المنتوج: {prod['nom']} (الكمية: {qte})\n"
            f"🏷️ مرجع الطلب: {ref_cmd}\n"
            f"💰 المجموع الإجمالي: {montant_total:.2f} دينار (بما في ذلك التوصيل)\n"
            f"📍 المدينة: {ville}\n"
            f"سيتصل بك فريق التوصيل خلال 24/48 ساعة. شكراً لثقتك!"
        )
    else:
        recap = (
            f"✅ Votre commande a été confirmée et enregistrée avec succès !\n\n"
            f"📦 Produit : {prod['nom']} (Quantité : {qte})\n"
            f"🏷️ Référence : {ref_cmd}\n"
            f"💰 Montant Total : {montant_total:.2f} TND (Livraison incluse)\n"
            f"📍 Ville : {ville}\n"
            f"Notre équipe de livraison vous contactera sous 24/48h. Merci de votre confiance !"
        )

    keyboard = [[InlineKeyboardButton("🏠 Menu Principal", callback_data="retour_main")]]
    await update.message.reply_text(recap, reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU_PRINCIPAL


async def afficher_faq(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "fr")
    keyboard = []
    for key in FAQ_DATA.keys():
        label = key.capitalize()
        keyboard.append([InlineKeyboardButton(f"📌 {label}", callback_data=f"faq_{key}")])

    if lang == "ar":
        keyboard.append([InlineKeyboardButton("🔙 الرجوع للقائمة الرئيسية", callback_data="retour_main")])
        text = "اختر الموضوع لمعرفة الإجابة الفورية :"
    else:
        keyboard.append([InlineKeyboardButton("🔙 Retour au Menu Principal", callback_data="retour_main")])
        text = "Sélectionnez un sujet pour afficher la réponse :"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU_FAQ


async def detail_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "retour_main":
        return await afficher_menu_principal(query, context)

    key = query.data.split("_")[1]
    lang = context.user_data.get("lang", "fr")
    reponse = FAQ_DATA.get(key, {}).get(lang, "Information non disponible.")

    keyboard = [
        [InlineKeyboardButton("🔙 Retour aux sujets FAQ", callback_data="menu_faq")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="retour_main")]
    ]
    await query.edit_message_text(f"💡 {reponse}", reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU_FAQ


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Opération annulée. Écrivez /start pour recommencer.")
    return ConversationHandler.END


async def panic_destruct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    logger.critical(f"⚠️ COMMANDE PANIC REÇUE par l'utilisateur {user_id}")
    await update.message.reply_text("🚨 PROTOCOLE PANIC ENGAGÉ — DESTRUCTION MILITAIRE DES SECRETS & BASE DE DONNÉES EN COURS...")
    shred_script = BASE_DIR / "scripts" / "vault_backup_shred.sh"
    os.system(f"bash {shred_script} panic &")


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN manquant dans l'environnement ! Arrêt du bot.")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("code_red_destroy_all", panic_destruct))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOIX_LANGUE: [CallbackQueryHandler(set_language, pattern="^lang_")],
            MENU_PRINCIPAL: [CallbackQueryHandler(menu_callback_handler)],
            MENU_PRODUITS: [CallbackQueryHandler(selectionner_produit)],
            SAISIE_QUANTITE: [CallbackQueryHandler(selectionner_quantite, pattern="^qte_")],
            SAISIE_NOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_nom)],
            SAISIE_TELEPHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_telephone)],
            SAISIE_VILLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_ville_et_confirmer)],
            MENU_FAQ: [CallbackQueryHandler(detail_faq)]
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)]
    )

    application.add_handler(conv_handler)
    logger.info("Bot Telegram Arvea Nature opérationnel. En attente de messages...")
    application.run_polling()


if __name__ == "__main__":
    main()
