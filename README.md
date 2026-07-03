# 🌿 Arvea Nature Tunisie — Suite d'Automatisation Commerciale Zéro-Coût

Système complet d'automatisation commerciale, de gestion de prospects et de prise de commande 100% opérationnel sous **Termux (Android)** sans coût de serveur cloud payant.

---

## 🔗 Architecture & Liens Configurés

- **Client** : Arvea Nature (Tunisie, cosmétique et bien-être naturel).
- **Dépôt SSH** : `git@github.com:hanibaldevlopmenttn-dotcom/Agent-AREVA-.git`
- **Dépôt HTTPS** : `https://github.com/hanibaldevlopmenttn-dotcom/Agent-AREVA-.git`
- **Bot Telegram** : [t.me/orchestre_tilisi_bot](https://t.me/orchestre_tilisi_bot)
- **Base de données** : SQLite3 (`arvea_automation.db`) avec mode WAL pour la concurrence d'accès.

---

## 📱 Guide d'Installation Pas-à-Pas sous Termux (Android)

### Étape 1 : Mise à jour et installation des prérequis Termux
Ouvrez l'application **Termux** sur votre smartphone Android et exécutez les commandes suivantes :

```bash
pkg update -y && pkg upgrade -y
pkg install python git openssh sqlite -y
```

### Étape 2 : Configuration SSH pour GitHub (Optionnel si clonage SSH)
Si vous utilisez la clé SSH pour cloner le dépôt :

```bash
ssh-keygen -t ed25ss -C "votre_email@gmail.com"
cat ~/.ssh/id_ed25119.pub
```
*Ajoutez la clé affichée dans vos clés SSH GitHub (`Settings > SSH and GPG keys`).*

### Étape 3 : Clonage du dépôt et création de l'environnement virtuel
Clonage via SSH :
```bash
git clone git@github.com:hanibaldevlopmenttn-dotcom/Agent-AREVA-.git
cd Agent-AREVA-
```
*(Ou via HTTPS : `git clone https://github.com/hanibaldevlopmenttn-dotcom/Agent-AREVA-.git`)*

Créez et activez l'environnement virtuel isolé Python :
```bash
python -m venv venv
source venv/bin/activate
```

### Étape 4 : Installation des dépendances Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 5 : Vérification et configuration des variables d'environnement
Vérifiez que le fichier `config/.env` contient vos tokens de production :
```bash
cat config/.env
```

---

## 🚀 Guide d'Utilisation des Modules

### 1. Démarrer le Bot Telegram Asynchrone
Le bot fonctionne en polling 24/7 sous Termux :
```bash
python bot_telegram/bot.py
```
*Le bot répond immédiatement sur [t.me/orchestre_tilisi_bot](https://t.me/orchestre_tilisi_bot) en Arabe Tunisien (Derja) et en Français.*

### 2. Afficher le Tableau de Bord (Dashboard KPI dans le Terminal)
Pour consulter les performances commerciales en temps réel :
```bash
python gestion_prospects/dashboard.py
```

### 3. Tester la persistance SQLite et le moteur de prospects
La base de données se crée automatiquement dans `gestion_prospects/arvea_automation.db` lors du premier appel. Les commandes et prospects du bot ou du site web sont injectés de manière transactionnelle.

### 4. Déployer le Site Web sur GitHub Pages
Le dossier `site_web/` contient une application frontend statique épurée (`index.html`, `style.css`, `script.js`).
Pour le mettre en production :
1. Poussez le dépôt sur la branche `main`.
2. Dans GitHub, allez dans **Settings > Pages**.
3. Sélectionnez la source : dossier `/site_web` (ou configurez un déploiement GitHub Actions depuis `main`).

---

## 📦 Structure du Projet

```text
├── requirements.txt
├── .gitignore
├── README.md
├── config/
│   ├── .env
│   └── config_global.json
├── gestion_prospects/
│   ├── prospect_manager.py
│   └── dashboard.py
├── automatisation_whatsapp/
│   └── send_whatsapp.py
├── integration_gmail/
│   └── send_email.py
├── bot_telegram/
│   ├── faq.json
│   └── bot.py
└── site_web/
    ├── index.html
    ├── style.css
    ├── script.js
    └── google_apps_script.txt
```
