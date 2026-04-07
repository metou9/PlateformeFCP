#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from formulaire.models import Wilaya, Moughataa, Commune, Paysage, Village, SousProjet
from django.db import transaction

@transaction.atomic
def import_all():
    print("🚀 IMPORTATION DES DONNÉES DU DOCUMENT (uniquement)")
    print("=" * 60)
    
    # 1. Supprimer les sous-projets (clés étrangères)
    print("🗑️  Suppression des sous-projets existants...")
    sous_projets_count = SousProjet.objects.count()
    SousProjet.objects.all().delete()
    print(f"   ✅ {sous_projets_count} sous-projets supprimés")
    
    # 2. Supprimer les autres données
    print("🗑️  Suppression des anciennes données...")
    Village.objects.all().delete()
    Paysage.objects.all().delete()
    Commune.objects.all().delete()
    Moughataa.objects.all().delete()
    Wilaya.objects.all().delete()
    print("   ✅ Toutes les localités supprimées")
    
    # Structure des données
    data = [
        {
            "wilaya": "Gorgol",
            "moughataa": "M'Bout",
            "commune": "Edebaye Ehel Guelaye",
            "paysage": "Djeibaba",
            "villages": ["Djeibaba", "Nhal", "Guediama 1", "Guediama 2"]
        },
        {
            "wilaya": "Gorgol",
            "moughataa": "Monguel",
            "commune": "Bokel",
            "paysage": "Evedjar Ehel Cheikh",
            "villages": ["Khmoumeini", "Ewmarly", "Vilke 1", "Vilke 2", "Codiwar", "Zbil", "Mbout"]
        },
        {
            "wilaya": "Assaba",
            "moughataa": "Barkewol",
            "commune": "Rdheydia",
            "paysage": "Lehneikatt",
            "villages": ["Lehneykatt", "Eguinni", "Levrea", "Liksar 1", "Liksar 2", "Machrou", "Oulad maham", "Rdheidhi"]
        },
        {
            "wilaya": "Assaba",
            "moughataa": "Kankossa",
            "commune": "Hamod",
            "paysage": "Oudey Talaba",
            "villages": ["Agwanite", "Guido", "Oudey Talaba 1", "Oudey Talaba 2", "Nezah"]
        },
        {
            "wilaya": "Brakna",
            "moughataa": "Maghtaà Lahjar",
            "commune": "Sangrava",
            "paysage": "Eguerj III",
            "villages": ["Eguerj III", "Eguerj II", "Mayssara", "Machrouaa"]
        },
        {
            "wilaya": "Brakna",
            "moughataa": "Male",
            "commune": "Male",
            "paysage": "Sagh El Mohr",
            "villages": ["Sagh Moher 1", "Sagh Moher 2", "Jektoub", "Abneir"]
        },
        {
            "wilaya": "Brakna",
            "moughataa": "Bababé",
            "commune": "Bababé",
            "paysage": "Bababé",
            "villages": []
        },
        {
            "wilaya": "Brakna",
            "moughataa": "Boghé",
            "commune": "Boghé",
            "paysage": "CPB Extension",
            "villages": []
        },
        {
            "wilaya": "Trarza",
            "moughataa": "Keur Macène",
            "commune": "Mbalal",
            "paysage": "Canal Aftout Essahili",
            "villages": []
        },
    ]
    
    wilayas_dict = {}
    moughataas_dict = {}
    communes_dict = {}
    
    print("\n📌 Création des wilayas, moughataas, communes, paysages et villages...")
    
    wilaya_count = 0
    moughataa_count = 0
    commune_count = 0
    paysage_count = 0
    village_count = 0
    
    for item in data:
        # Wilaya : code = nom (unique)
        wilaya_nom = item["wilaya"]
        if wilaya_nom not in wilayas_dict:
            wilaya, created = Wilaya.objects.get_or_create(
                code=wilaya_nom,
                defaults={"nom": wilaya_nom}
            )
            wilayas_dict[wilaya_nom] = wilaya
            if created:
                wilaya_count += 1
                print(f"  ✅ Wilaya: {wilaya.nom}")
        
        # Moughataa
        moughataa_nom = item["moughataa"]
        key_m = (wilaya_nom, moughataa_nom)
        if key_m not in moughataas_dict:
            moughataa, created = Moughataa.objects.get_or_create(
                nom=moughataa_nom,
                wilaya=wilayas_dict[wilaya_nom]
            )
            moughataas_dict[key_m] = moughataa
            if created:
                moughataa_count += 1
                print(f"    📌 Moughataa: {moughataa.nom}")
        
        # Commune
        commune_nom = item["commune"]
        key_c = (wilaya_nom, moughataa_nom, commune_nom)
        if key_c not in communes_dict:
            commune, created = Commune.objects.get_or_create(
                nom=commune_nom,
                moughataa=moughataas_dict[key_m]
            )
            communes_dict[key_c] = commune
            if created:
                commune_count += 1
                print(f"      📍 Commune: {commune.nom}")
        
        # Paysage
        paysage_nom = item["paysage"]
        paysage, created = Paysage.objects.get_or_create(
            nom=paysage_nom,
            commune=communes_dict[key_c]
        )
        if created:
            paysage_count += 1
            print(f"        🌳 Paysage: {paysage.nom}")
        
        # Villages
        for village_nom in item["villages"]:
            village, created = Village.objects.get_or_create(
                nom=village_nom,
                paysage=paysage
            )
            if created:
                village_count += 1
                print(f"          🏡 Village: {village.nom}")
    
    # ============================================
    # RÉSULTATS
    # ============================================
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT FINAL")
    print("=" * 60)
    print(f"🏛️  Wilayas créées: {wilaya_count}")
    print(f"📌 Moughataas créées: {moughataa_count}")
    print(f"📍 Communes créées: {commune_count}")
    print(f"🌳 Paysages créés: {paysage_count}")
    print(f"🏡 Villages créés: {village_count}")
    
    print("\n🔍 DÉTAIL PAR WILAYA:")
    for wilaya in Wilaya.objects.all().order_by('nom'):
        nb_m = wilaya.moughataas.count()
        nb_c = Commune.objects.filter(moughataa__wilaya=wilaya).count()
        nb_p = Paysage.objects.filter(commune__moughataa__wilaya=wilaya).count()
        nb_v = Village.objects.filter(paysage__commune__moughataa__wilaya=wilaya).count()
        print(f"  {wilaya.nom}: {nb_m} moughataas, {nb_c} communes, {nb_p} paysages, {nb_v} villages")

if __name__ == "__main__":
    import_all()