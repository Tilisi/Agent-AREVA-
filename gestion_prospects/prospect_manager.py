import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / "config" / ".env"
if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)

DEFAULT_DB_PATH = BASE_DIR / "gestion_prospects" / "arvea_automation.db"
DB_PATH_STR = os.getenv("DATABASE_PATH")
if DB_PATH_STR:
    DB_PATH = Path(DB_PATH_STR)
    if not DB_PATH.is_absolute():
        DB_PATH = BASE_DIR / DB_PATH
else:
    DB_PATH = DEFAULT_DB_PATH


class ProspectManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=FULL;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_complet TEXT NOT NULL,
                    telephone TEXT UNIQUE NOT NULL,
                    ville TEXT,
                    langue TEXT DEFAULT 'fr',
                    canal_source TEXT DEFAULT 'telegram',
                    date_inscription TEXT NOT NULL,
                    statut TEXT DEFAULT 'nouveau'
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prospect_id INTEGER NOT NULL,
                    reference_commande TEXT UNIQUE NOT NULL,
                    produits_json TEXT NOT NULL,
                    montant_total REAL NOT NULL,
                    frais_livraison REAL DEFAULT 7.0,
                    statut_commande TEXT DEFAULT 'en_attente',
                    date_commande TEXT NOT NULL,
                    FOREIGN KEY (prospect_id) REFERENCES prospects(id) ON DELETE CASCADE
                );
            """)
            conn.commit()

    def verify_integrity(self) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            row = cursor.fetchone()
            return row and row[0] == "ok"

    def ajouter_ou_mettre_a_jour_prospect(self, nom_complet: str, telephone: str, ville: str = "Inconnue", langue: str = "fr", canal_source: str = "telegram") -> int:
        clean_phone = telephone.strip().replace(" ", "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM prospects WHERE telephone = ?", (clean_phone,))
            row = cursor.fetchone()
            if row:
                prospect_id = int(row["id"])
                cursor.execute("""
                    UPDATE prospects
                    SET nom_complet = ?, ville = ?, langue = ?
                    WHERE id = ?
                """, (nom_complet, ville, langue, prospect_id))
            else:
                cursor.execute("""
                    INSERT INTO prospects (nom_complet, telephone, ville, langue, canal_source, date_inscription, statut)
                    VALUES (?, ?, ?, ?, ?, ?, 'actif')
                """, (nom_complet, clean_phone, ville, langue, canal_source, now))
                prospect_id = cursor.lastrowid
            conn.commit()
            return prospect_id

    def creer_commande(self, prospect_id: int, produits_json: str, montant_total: float, frais_livraison: float = 7.0) -> str:
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        ref_code = f"ARV-{now.strftime('%Y%m%d%H%M%S')}-{prospect_id}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO commandes (prospect_id, reference_commande, produits_json, montant_total, frais_livraison, statut_commande, date_commande)
                VALUES (?, ?, ?, ?, ?, 'confirmee', ?)
            """, (prospect_id, ref_code, produits_json, montant_total, frais_livraison, timestamp_str))
            conn.commit()
        return ref_code

    def get_prospect_by_phone(self, telephone: str) -> Optional[Dict[str, Any]]:
        clean_phone = telephone.strip().replace(" ", "")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prospects WHERE telephone = ?", (clean_phone,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def lister_prospects(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prospects ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]

    def lister_commandes(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, p.nom_complet, p.telephone, p.ville
                FROM commandes c
                JOIN prospects p ON c.prospect_id = p.id
                ORDER BY c.id DESC
            """)
            return [dict(r) for r in cursor.fetchall()]

    def get_kpi_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total_prospects FROM prospects")
            total_prospects = cursor.fetchone()["total_prospects"]

            cursor.execute("SELECT COUNT(*) as total_commandes, IFNULL(SUM(montant_total), 0.0) as ca_total FROM commandes")
            row_cmd = cursor.fetchone()
            total_commandes = row_cmd["total_commandes"]
            ca_total = row_cmd["ca_total"]

            cursor.execute("""
                SELECT statut_commande, COUNT(*) as count
                FROM commandes
                GROUP BY statut_commande
            """)
            statuts = {row["statut_commande"]: row["count"] for row in cursor.fetchall()}

            conversion_rate = (total_commandes / total_prospects * 100.0) if total_prospects > 0 else 0.0

            return {
                "total_prospects": total_prospects,
                "total_commandes": total_commandes,
                "chiffre_affaires_tnd": round(ca_total, 2),
                "taux_conversion_pct": round(conversion_rate, 2),
                "repartition_statuts": statuts
            }
