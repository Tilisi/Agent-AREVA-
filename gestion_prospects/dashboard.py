import sys
from pathlib import Path
from tabulate import tabulate

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from gestion_prospects.prospect_manager import ProspectManager


def afficher_dashboard() -> None:
    pm = ProspectManager()
    stats = pm.get_kpi_stats()

    print("\n" + "="*60)
    print("🌿  TABLEAU DE BORD COMMERCIAL - ARVEA NATURE TUNISIE  🌿")
    print("="*60)

    kpi_table = [
        ["Total Prospects Enregistrés", f"{stats['total_prospects']}"],
        ["Total Commandes Confirmées", f"{stats['total_commandes']}"],
        ["Chiffre d'Affaires Généré", f"{stats['chiffre_affaires_tnd']:.2f} TND"],
        ["Taux de Conversion", f"{stats['taux_conversion_pct']:.2f} %"]
    ]
    print("\n--- INDICATEURS DE PERFORMANCE CLES (KPI) ---")
    print(tabulate(kpi_table, headers=["Indicateur", "Valeur Actuelle"], tablefmt="grid"))

    statuts = stats.get("repartition_statuts", {})
    if statuts:
        statut_table = [[st, cnt] for st, cnt in statuts.items()]
        print("\n--- REPARTITION DES COMMANDES PAR STATUT ---")
        print(tabulate(statut_table, headers=["Statut Commande", "Nombre"], tablefmt="simple"))

    prospects = pm.lister_prospects()[:5]
    if prospects:
        p_table = [
            [p["id"], p["nom_complet"], p["telephone"], p["ville"], p["langue"], p["date_inscription"]]
            for p in prospects
        ]
        print("\n--- 5 DERNIERS PROSPECTS INSCRITS ---")
        print(tabulate(p_table, headers=["ID", "Nom & Prénom", "Téléphone", "Ville", "Langue", "Date Inscription"], tablefmt="psql"))

    commandes = pm.lister_commandes()[:5]
    if commandes:
        c_table = [
            [c["reference_commande"], c["nom_complet"], c["telephone"], f"{c['montant_total']:.2f} TND", c["statut_commande"], c["date_commande"]]
            for c in commandes
        ]
        print("\n--- 5 DERNIERES COMMANDES ---")
        print(tabulate(c_table, headers=["Référence", "Client", "Téléphone", "Montant", "Statut", "Date"], tablefmt="psql"))

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    afficher_dashboard()
