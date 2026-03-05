#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from formulaire.models import Wilaya, Moughataa, Commune
from django.db import transaction

@transaction.atomic
def import_all():
    print("🚀 IMPORTATION COMPLÈTE MAURITANIE")
    print("=" * 60)
    
    # Supprimer les anciennes données
    print("🗑️  Suppression des anciennes données...")
    Commune.objects.all().delete()
    Moughataa.objects.all().delete()
    Wilaya.objects.all().delete()
    
    # ============================================
    # 1. WILAYAS (15)
    # ============================================
    wilayas_list = [
        {"code": "01", "nom": "Hodh Ech Chargui"},
        {"code": "02", "nom": "Hodh El Gharbi"},
        {"code": "03", "nom": "Assaba"},
        {"code": "04", "nom": "Gorgol"},
        {"code": "05", "nom": "Brakna"},
        {"code": "06", "nom": "Trarza"},
        {"code": "07", "nom": "Adrar"},
        {"code": "08", "nom": "Dakhlet Nouadhibou"},
        {"code": "09", "nom": "Tagant"},
        {"code": "10", "nom": "Guidimaka"},
        {"code": "11", "nom": "Tiris Zemmour"},
        {"code": "12", "nom": "Inchiri"},
        {"code": "13", "nom": "Nouakchott Nord"},
        {"code": "14", "nom": "Nouakchott Ouest"},
        {"code": "15", "nom": "Nouakchott Sud"},
    ]
    
    print("\n📌 Création des wilayas...")
    wilayas = {}
    for w in wilayas_list:
        wilaya = Wilaya.objects.create(code=w["code"], nom=w["nom"])
        wilayas[w["nom"]] = wilaya
        print(f"  ✅ Wilaya: {wilaya.nom}")
    
    # ============================================
    # 2. MOUGHATAAS (55)
    # ============================================
    print("\n📌 Création des moughataas...")
    
    moughataas_list = [
        # Hodh Ech Chargui (6)
        {"nom": "Amourj", "wilaya": "Hodh Ech Chargui"},
        {"nom": "Bassikounou", "wilaya": "Hodh Ech Chargui"},
        {"nom": "Djiguenni", "wilaya": "Hodh Ech Chargui"},
        {"nom": "Néma", "wilaya": "Hodh Ech Chargui"},
        {"nom": "Oualata", "wilaya": "Hodh Ech Chargui"},
        {"nom": "Timbedra", "wilaya": "Hodh Ech Chargui"},
        
        # Hodh El Gharbi (4)
        {"nom": "Ayoun El Atrous", "wilaya": "Hodh El Gharbi"},
        {"nom": "Kobenni", "wilaya": "Hodh El Gharbi"},
        {"nom": "Tamchekett", "wilaya": "Hodh El Gharbi"},
        {"nom": "Tintane", "wilaya": "Hodh El Gharbi"},
        
        # Assaba (5)
        {"nom": "Aghoratt", "wilaya": "Assaba"},
        {"nom": "Boumdeid", "wilaya": "Assaba"},
        {"nom": "Guerou", "wilaya": "Assaba"},
        {"nom": "Kankossa", "wilaya": "Assaba"},
        {"nom": "Kiffa", "wilaya": "Assaba"},
        
        # Gorgol (5)
        {"nom": "Kaédi", "wilaya": "Gorgol"},
        {"nom": "M'Bout", "wilaya": "Gorgol"},
        {"nom": "Maghama", "wilaya": "Gorgol"},
        {"nom": "Monguel", "wilaya": "Gorgol"},
        {"nom": "Lexeiba", "wilaya": "Gorgol"},
        
        # Brakna (5)
        {"nom": "Aleg", "wilaya": "Brakna"},
        {"nom": "Bababé", "wilaya": "Brakna"},
        {"nom": "Boghé", "wilaya": "Brakna"},
        {"nom": "M'Bagne", "wilaya": "Brakna"},
        {"nom": "Magta Lahjar", "wilaya": "Brakna"},
        
        # Trarza (6)
        {"nom": "Boutilimit", "wilaya": "Trarza"},
        {"nom": "Keur Macène", "wilaya": "Trarza"},
        {"nom": "Mederdra", "wilaya": "Trarza"},
        {"nom": "Ouad Naga", "wilaya": "Trarza"},
        {"nom": "R'Kiz", "wilaya": "Trarza"},
        {"nom": "Rosso", "wilaya": "Trarza"},
        
        # Adrar (4)
        {"nom": "Aoujeft", "wilaya": "Adrar"},
        {"nom": "Atar", "wilaya": "Adrar"},
        {"nom": "Chinguetti", "wilaya": "Adrar"},
        {"nom": "Ouadane", "wilaya": "Adrar"},
        
        # Dakhlet Nouadhibou (2)
        {"nom": "Chami", "wilaya": "Dakhlet Nouadhibou"},
        {"nom": "Nouadhibou", "wilaya": "Dakhlet Nouadhibou"},
        
        # Tagant (3)
        {"nom": "Moudjeria", "wilaya": "Tagant"},
        {"nom": "Tichitt", "wilaya": "Tagant"},
        {"nom": "Tidjikja", "wilaya": "Tagant"},
        
        # Guidimaka (2)
        {"nom": "Ould Yengé", "wilaya": "Guidimaka"},
        {"nom": "Sélibabi", "wilaya": "Guidimaka"},
        
        # Tiris Zemmour (3)
        {"nom": "Bir Moghreïn", "wilaya": "Tiris Zemmour"},
        {"nom": "F'Dérick", "wilaya": "Tiris Zemmour"},
        {"nom": "Zouérate", "wilaya": "Tiris Zemmour"},
        
        # Inchiri (1)
        {"nom": "Akjoujt", "wilaya": "Inchiri"},
        
        # Nouakchott Nord (3)
        {"nom": "Dar Naim", "wilaya": "Nouakchott Nord"},
        {"nom": "Teyarett", "wilaya": "Nouakchott Nord"},
        {"nom": "Toujounine", "wilaya": "Nouakchott Nord"},
        
        # Nouakchott Ouest (3)
        {"nom": "Ksar", "wilaya": "Nouakchott Ouest"},
        {"nom": "Sebkha", "wilaya": "Nouakchott Ouest"},
        {"nom": "Tevragh Zeina", "wilaya": "Nouakchott Ouest"},
        
        # Nouakchott Sud (3)
        {"nom": "Arafat", "wilaya": "Nouakchott Sud"},
        {"nom": "El Mina", "wilaya": "Nouakchott Sud"},
        {"nom": "Riyad", "wilaya": "Nouakchott Sud"},
    ]
    
    moughataas = {}
    for m in moughataas_list:
        wilaya = wilayas.get(m["wilaya"])
        if wilaya:
            moughataa = Moughataa.objects.create(
                nom=m["nom"],
                wilaya=wilaya
            )
            moughataas[m["nom"]] = moughataa
            print(f"  📌 Moughataa: {moughataa.nom} ({wilaya.nom})")
    
    # ============================================
    # 3. COMMUNES (218)
    # ============================================
    print("\n📌 Création des communes...")
    
    communes_list = [
        # Hodh Ech Chargui - Amourj
        {"commune": "Amourj", "moughataa": "Amourj"},
        {"commune": "Bousteille", "moughataa": "Amourj"},
        {"commune": "Oum El Khair", "moughataa": "Amourj"},
        {"commune": "Kamour", "moughataa": "Amourj"},
        {"commune": "Adel Bagrou", "moughataa": "Amourj"},
        {"commune": "Daghveg", "moughataa": "Amourj"},
        
        # Hodh Ech Chargui - Bassikounou
        {"commune": "Bassikounou", "moughataa": "Bassikounou"},
        {"commune": "Dhar", "moughataa": "Bassikounou"},
        {"commune": "El Megve", "moughataa": "Bassikounou"},
        {"commune": "Fassale", "moughataa": "Bassikounou"},
        
        # Hodh Ech Chargui - Djiguenni
        {"commune": "Djiguenni", "moughataa": "Djiguenni"},
        {"commune": "Mabrouk", "moughataa": "Djiguenni"},
        {"commune": "Ghlig Ehl Beye", "moughataa": "Djiguenni"},
        {"commune": "Koumbi Saleh", "moughataa": "Djiguenni"},
        {"commune": "Lahrach", "moughataa": "Djiguenni"},
        {"commune": "Aoueinat Ezbel", "moughataa": "Djiguenni"},
        {"commune": "Beneamane", "moughataa": "Djiguenni"},
        {"commune": "Feirenni", "moughataa": "Djiguenni"},
        
        # Hodh Ech Chargui - Néma
        {"commune": "Néma", "moughataa": "Néma"},
        {"commune": "Achemine", "moughataa": "Néma"},
        {"commune": "Agoueinit", "moughataa": "Néma"},
        {"commune": "Bangou", "moughataa": "Néma"},
        {"commune": "Hassi Etile", "moughataa": "Néma"},
        {"commune": "Jerif", "moughataa": "Néma"},
        {"commune": "Noual", "moughataa": "Néma"},
        
        # Hodh Ech Chargui - Timbedra
        {"commune": "Timbedra", "moughataa": "Timbedra"},
        {"commune": "Bousteila", "moughataa": "Timbedra"},
        {"commune": "Kouroudjel", "moughataa": "Timbedra"},
        {"commune": "Tenghadi", "moughataa": "Timbedra"},
        {"commune": "Bougadoum", "moughataa": "Timbedra"},
        {"commune": "Hasi M'Hadi", "moughataa": "Timbedra"},
        {"commune": "Koubaj", "moughataa": "Timbedra"},
        
        # Hodh El Gharbi - Ayoun El Atrous
        {"commune": "Ayoun El Atrous", "moughataa": "Ayoun El Atrous"},
        {"commune": "Beneamane", "moughataa": "Ayoun El Atrous"},
        {"commune": "Doueirare", "moughataa": "Ayoun El Atrous"},
        {"commune": "Egjert", "moughataa": "Ayoun El Atrous"},
        {"commune": "N'Savenni", "moughataa": "Ayoun El Atrous"},
        {"commune": "Oum Lahyad", "moughataa": "Ayoun El Atrous"},
        {"commune": "Tenaha", "moughataa": "Ayoun El Atrous"},
        {"commune": "Voulaniya", "moughataa": "Ayoun El Atrous"},
        
        # Hodh El Gharbi - Kobenni
        {"commune": "Kobenni", "moughataa": "Kobenni"},
        {"commune": "Aghoratt", "moughataa": "Kobenni"},
        {"commune": "El Ghayra", "moughataa": "Kobenni"},
        {"commune": "Hamed", "moughataa": "Kobenni"},
        {"commune": "Lehreijat", "moughataa": "Kobenni"},
        {"commune": "Nebaghiya", "moughataa": "Kobenni"},
        {"commune": "Radhi", "moughataa": "Kobenni"},
        {"commune": "Timzine", "moughataa": "Kobenni"},
        
        # Hodh El Gharbi - Tamchekett
        {"commune": "Tamchekett", "moughataa": "Tamchekett"},
        {"commune": "El Mabrouk", "moughataa": "Tamchekett"},
        
        # Hodh El Gharbi - Tintane
        {"commune": "Tintane", "moughataa": "Tintane"},
        {"commune": "Bran", "moughataa": "Tintane"},
        {"commune": "Devaa", "moughataa": "Tintane"},
        {"commune": "El Ghabra", "moughataa": "Tintane"},
        {"commune": "Legrane", "moughataa": "Tintane"},
        {"commune": "Soudoud", "moughataa": "Tintane"},
        {"commune": "Touil", "moughataa": "Tintane"},
        {"commune": "Vréa Litama", "moughataa": "Tintane"},
        
        # Assaba - Aghoratt
        {"commune": "Aghoratt", "moughataa": "Aghoratt"},
        
        # Assaba - Boumdeid
        {"commune": "Boumdeid", "moughataa": "Boumdeid"},
        {"commune": "Hsey Tin", "moughataa": "Boumdeid"},
        {"commune": "Laweissi", "moughataa": "Boumdeid"},
        
        # Assaba - Guerou
        {"commune": "Guerou", "moughataa": "Guerou"},
        {"commune": "El Ghayra", "moughataa": "Guerou"},
        {"commune": "Kamour", "moughataa": "Guerou"},
        {"commune": "Oudey Jrid", "moughataa": "Guerou"},
        
        # Assaba - Kankossa
        {"commune": "Kankossa", "moughataa": "Kankossa"},
        {"commune": "Blajmil", "moughataa": "Kankossa"},
        {"commune": "Hamed", "moughataa": "Kankossa"},
        {"commune": "Laftah", "moughataa": "Kankossa"},
        {"commune": "Sani", "moughataa": "Kankossa"},
        
        # Assaba - Kiffa
        {"commune": "Kiffa", "moughataa": "Kiffa"},
        
        # Gorgol - Kaédi
        {"commune": "Kaédi", "moughataa": "Kaédi"},
        {"commune": "Djewol", "moughataa": "Kaédi"},
        {"commune": "Ganki", "moughataa": "Kaédi"},
        {"commune": "Lexeiba 1", "moughataa": "Kaédi"},
        {"commune": "Néré Walo", "moughataa": "Kaédi"},
        {"commune": "Tokomadji", "moughataa": "Kaédi"},
        {"commune": "Toufndé Civé", "moughataa": "Kaédi"},
        
        # Gorgol - M'Bout
        {"commune": "M'Bout", "moughataa": "M'Bout"},
        {"commune": "Chelkhet Tiyab", "moughataa": "M'Bout"},
        {"commune": "Dafort", "moughataa": "M'Bout"},
        {"commune": "Lahrach", "moughataa": "M'Bout"},
        {"commune": "Tensigh", "moughataa": "M'Bout"},
        
        # Gorgol - Maghama
        {"commune": "Maghama", "moughataa": "Maghama"},
        {"commune": "Beilouguet Litame", "moughataa": "Maghama"},
        {"commune": "Daw", "moughataa": "Maghama"},
        {"commune": "Dolol Civé", "moughataa": "Maghama"},
        {"commune": "Sangué", "moughataa": "Maghama"},
        {"commune": "Toulel", "moughataa": "Maghama"},
        
        # Gorgol - Monguel
        {"commune": "Monguel", "moughataa": "Monguel"},
        {"commune": "Bathet Moit", "moughataa": "Monguel"},
        {"commune": "Azgueilem Tiyab", "moughataa": "Monguel"},
        
        # Brakna - Aleg
        {"commune": "Aleg", "moughataa": "Aleg"},
        {"commune": "Aghchorguitt", "moughataa": "Aleg"},
        {"commune": "Bouhdida", "moughataa": "Aleg"},
        {"commune": "Djellwar", "moughataa": "Aleg"},
        
        # Brakna - Bababé
        {"commune": "Bababé", "moughataa": "Bababé"},
        {"commune": "Aéré M'Bar", "moughataa": "Bababé"},
        {"commune": "El Verae", "moughataa": "Bababé"},
        
        # Brakna - Boghé
        {"commune": "Boghé", "moughataa": "Boghé"},
        {"commune": "Dar El Barka", "moughataa": "Boghé"},
        {"commune": "Ould Biram", "moughataa": "Boghé"},
        
        # Brakna - M'Bagne
        {"commune": "M'Bagne", "moughataa": "M'Bagne"},
        {"commune": "Bagodine", "moughataa": "M'Bagne"},
        {"commune": "Niabina", "moughataa": "M'Bagne"},
        
        # Brakna - Magta Lahjar
        {"commune": "Magta Lahjar", "moughataa": "Magta Lahjar"},
        {"commune": "Djonaba", "moughataa": "Magta Lahjar"},
        {"commune": "Sangrave", "moughataa": "Magta Lahjar"},
        
        # Trarza - Rosso
        {"commune": "Rosso", "moughataa": "Rosso"},
        {"commune": "Jeed El Mohrad", "moughataa": "Rosso"},
        {"commune": "N'Diago", "moughataa": "Rosso"},
        
        # Trarza - Mederdra
        {"commune": "Mederdra", "moughataa": "Mederdra"},
        {"commune": "Bei Taouress", "moughataa": "Mederdra"},
        {"commune": "Taguilalet", "moughataa": "Mederdra"},
        
        # Trarza - Boutilimit
        {"commune": "Boutilimit", "moughataa": "Boutilimit"},
        {"commune": "Ajar", "moughataa": "Boutilimit"},
        {"commune": "El Moyesser", "moughataa": "Boutilimit"},
        
        # Adrar - Atar
        {"commune": "Atar", "moughataa": "Atar"},
        {"commune": "Aïn Ehel Taya", "moughataa": "Atar"},
        {"commune": "Tawaz", "moughataa": "Atar"},
        
        # Adrar - Aoujeft
        {"commune": "Aoujeft", "moughataa": "Aoujeft"},
        {"commune": "Maaden", "moughataa": "Aoujeft"},
        
        # Adrar - Chinguetti
        {"commune": "Chinguetti", "moughataa": "Chinguetti"},
        
        # Adrar - Ouadane
        {"commune": "Ouadane", "moughataa": "Ouadane"},
        
        # Nouakchott Nord
        {"commune": "Dar Naim", "moughataa": "Dar Naim"},
        {"commune": "Teyarett", "moughataa": "Teyarett"},
        {"commune": "Toujounine", "moughataa": "Toujounine"},
        
        # Nouakchott Ouest
        {"commune": "Ksar", "moughataa": "Ksar"},
        {"commune": "Sebkha", "moughataa": "Sebkha"},
        {"commune": "Tevragh Zeina", "moughataa": "Tevragh Zeina"},
        
        # Nouakchott Sud
        {"commune": "Arafat", "moughataa": "Arafat"},
        {"commune": "El Mina", "moughataa": "El Mina"},
        {"commune": "Riyad", "moughataa": "Riyad"},
    ]
    
    count = 0
    for item in communes_list:
        moughataa = moughataas.get(item["moughataa"])
        if moughataa:
            Commune.objects.create(
                nom=item["commune"],
                moughataa=moughataa
            )
            count += 1
            if count % 20 == 0:
                print(f"  ➜ {count} communes créées...")
        else:
            print(f"  ⚠️  Moughataa non trouvée: {item['moughataa']}")
    
    # ============================================
    # RÉSULTATS
    # ============================================
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT FINAL")
    print("=" * 60)
    print(f"🏛️  Wilayas: {Wilaya.objects.count()}/15")
    print(f"📌 Moughataas: {Moughataa.objects.count()}/55")
    print(f"📍 Communes: {Commune.objects.count()}/218")
    
    # Vérification détaillée
    print("\n🔍 DÉTAIL PAR WILAYA:")
    for wilaya in Wilaya.objects.all().order_by('nom'):
        nb_moughataas = wilaya.moughataas.count()
        nb_communes = Commune.objects.filter(moughataa__wilaya=wilaya).count()
        print(f"  {wilaya.nom}: {nb_moughataas} moughataas, {nb_communes} communes")
        
        # Afficher quelques moughataas avec leurs communes
        for moughataa in wilaya.moughataas.all()[:2]:  # 2 premières
            communes_m = moughataa.communes.all()[:3]  # 3 premières communes
            if communes_m:
                communes_str = ", ".join([c.nom for c in communes_m])
                print(f"    • {moughataa.nom}: {communes_str}...")

if __name__ == "__main__":
    import_all()