#!/usr/bin/env python3
"""
Script pour gérer les utilisateurs dans la table formulaire_utilisateur
Utilisation: python create_utilisateur.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialiser Django
django.setup()

from formulaire.models import Utilisateur, Wilaya

# Liste des utilisateurs à gérer
# IMPORTANT:
# - role doit être parmi: admin, agent, superviseur, consultant
# - wilaya_code doit correspondre au champ Wilaya.code en base
utilisateurs = [
    {
        'nom': 'Biha',
        'prenom': 'Aminetou',
        'username': 'aminab',
        'password': 'amina92',
        'role': 'superadmin',
        'email': 'aminab92@fcp.com',
        'actif': True,
        'wilaya_code': None
    },
    {
        'nom': 'Isselmou',
        'prenom': 'Iss',
        'username': 'admin1',
        'password': 'admin12',
        'role': 'admin',
        'email': 'admininit@fcp.com',
        'actif': True,
        'wilaya_code': None
    },
    {
        'nom': 'Ahmed Louli',
        'prenom': 'Nemine',
        'username': 'nemine',
        'password': 'nemine1224',
        'role': 'agent',
        'email': 'nemine@fcp.com',
        'actif': True,
        'wilaya_code': 'Gorgol'
    },
    {
        'nom': 'Maaloum',
        'prenom': 'Cheikh',
        'username': 'cheikhM',
        'password': 'cheikh5643',
        'role': 'agent',
        'email': 'cheikhm@fcp.com',
        'actif': True,
        'wilaya_code': 'Gorgol'
    },
    {
        'nom': 'Sidi Mohamed',
        'prenom': 'Cheikh',
        'username': 'cheikhS',
        'password': 'cheikh7896',
        'role': 'agent',
        'email': 'cheikhs@fcp.com',
        'actif': True,
        'wilaya_code': 'Gorgol'
    },
    {
        'nom': 'Comité',
        'prenom': 'Président',
        'username': 'presidGorgol',
        'password': 'Presid3456',
        'role': 'prescomite',
        'email': 'presidGorgol@fcp.com',
        'actif': True,
        'wilaya_code': 'Gorgol'
    },
     {
        'nom': 'Comité',
        'prenom': 'Président',
        'username': 'presidBrakna',
        'password': 'Presid7865',
        'role': 'prescomite',
        'email': 'presidBrakna@fcp.com',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
      {
        'nom': 'Comité',
        'prenom': 'Président',
        'username': 'presidTrarza',
        'password': 'Presid0987',
        'role': 'prescomite',
        'email': 'presidTrarza@fcp.com',
        'actif': True,
        'wilaya_code': 'Trarza'
    },
    {
        'nom': 'Comité',
        'prenom': 'Président',
        'username': 'presidAssaba',
        'password': 'Presid1489',
        'role': 'prescomite',
        'email': 'presidAssaba@fcp.com',
        'actif': True,
        'wilaya_code': 'Assaba'
    },
     {
        'nom': 'Mouhamed',
        'prenom': 'Aziz',
        'username': 'azizM',
        'password': 'aziz8866',
        'role': 'agent',
        'email': 'azizm@fcp.com',
        'actif': True,
        'wilaya_code': 'Assaba'
    },
    {
        'nom': 'Wele',
        'prenom': 'Mamadou',
        'username': 'mamadouW',
        'password': 'mamadou4452',
        'role': 'agent',
        'email': 'mamadouW@fcp.com',
        'actif': True,
        'wilaya_code': 'Assaba'
    },
     {
        'nom': 'Beddi',
        'prenom': 'Babah',
        'username': 'babah',
        'password': 'babah1224',
        'role': 'agent',
        'email': 'ouldbedy@gmail.com',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
      {
        'nom': 'Ahmed Salem',
        'prenom': 'El hacen',
        'username': 'hacen',
        'password': 'hacen3456',
        'role': 'agent',
        'email': 'elhassensalem@yahoo.fr',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
    {
        'nom': 'El Wely',
        'prenom': 'El houssein',
        'username': 'houssein',
        'password': 'houssein4789',
        'role': 'agent',
        'email': 'elhassensalem@yahoo.fr',
        'actif': True,
        'wilaya_code': 'Brakna'
    },

    {
        'nom': 'Ahmed Louli',
        'prenom': 'Nemine',
        'username': 'nemine2',
        'password': 'nemine1224',
        'role': 'agent',
        'email': 'nemine@fcp.com',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
    {
        'nom': 'Maaloum',
        'prenom': 'Cheikh',
        'username': 'cheikhM2',
        'password': 'cheikh5643',
        'role': 'agent',
        'email': 'cheikhm@fcp.com',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
    {
        'nom': 'Sidi Mohamed',
        'prenom': 'Cheikh',
        'username': 'cheikhS2',
        'password': 'cheikh7896',
        'role': 'agent',
        'email': 'cheikhs@fcp.com',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
]


def get_wilaya_from_code(wilaya_code):
    """Retourne la wilaya à partir de son code, ou None."""
    if not wilaya_code:
        return None

    wilaya = Wilaya.objects.filter(code=wilaya_code).first()
    if not wilaya:
        raise ValueError(f"Wilaya introuvable pour le code {wilaya_code}")
    return wilaya


def creer_utilisateur(data):
    """Crée un utilisateur s'il n'existe pas déjà."""
    try:
        if Utilisateur.objects.filter(username=data['username']).exists():
            print(f"⚠️  L'utilisateur {data['username']} existe déjà - Ignoré")
            return False

        wilaya = get_wilaya_from_code(data.get('wilaya_code'))

        utilisateur = Utilisateur(
            nom=data['nom'],
            prenom=data['prenom'],
            username=data['username'],
            email=data['email'],
            role=data['role'],
            wilaya=wilaya,
            actif=data.get('actif', True)
        )

        utilisateur.set_password(data['password'])
        utilisateur.save()

        print(
            f"✅ Utilisateur créé : {utilisateur.username} - "
            f"{utilisateur.prenom} {utilisateur.nom} ({utilisateur.role}) - "
            f"Wilaya: {utilisateur.wilaya.nom if utilisateur.wilaya else 'Aucune'}"
        )
        return True

    except Exception as e:
        print(f"❌ Erreur pour {data['username']} : {str(e)}")
        return False


def mettre_a_jour_utilisateur(data):
    """Met à jour un utilisateur existant."""
    try:
        utilisateur = Utilisateur.objects.filter(username=data['username']).first()
        if not utilisateur:
            print(f"⚠️  L'utilisateur {data['username']} n'existe pas - mise à jour impossible")
            return False

        wilaya = get_wilaya_from_code(data.get('wilaya_code'))

        utilisateur.nom = data['nom']
        utilisateur.prenom = data['prenom']
        utilisateur.email = data['email']
        utilisateur.role = data['role']
        utilisateur.wilaya = wilaya
        utilisateur.actif = data.get('actif', True)
        utilisateur.set_password(data['password'])
        utilisateur.save()

        print(
            f"🔁 Utilisateur mis à jour : {utilisateur.username} - "
            f"{utilisateur.prenom} {utilisateur.nom} ({utilisateur.role}) - "
            f"Wilaya: {utilisateur.wilaya.nom if utilisateur.wilaya else 'Aucune'}"
        )
        return True

    except Exception as e:
        print(f"❌ Erreur mise à jour pour {data['username']} : {str(e)}")
        return False


def supprimer_utilisateur(username):
    """Supprime un utilisateur précis."""
    try:
        user = Utilisateur.objects.get(username=username)
        user.delete()
        print(f"🗑️  Utilisateur supprimé : {username}")
        return True
    except Utilisateur.DoesNotExist:
        print(f"⚠️  Utilisateur {username} non trouvé")
        return False


def lister_utilisateurs():
    """Affiche tous les utilisateurs."""
    print("\n" + "=" * 60)
    print("Liste des utilisateurs dans la base :")
    print("=" * 60)
    for user in Utilisateur.objects.all().order_by('username'):
        print(
            f"  • {user.username} : {user.prenom} {user.nom} - "
            f"{user.get_role_display()} - "
            f"{'Actif' if user.actif else 'Inactif'}"
        )
    print("=" * 60)


def recreer_tous_les_utilisateurs():
    """Supprime puis recrée tous les utilisateurs présents dans le fichier."""
    print("\n📝 Recréation de tous les utilisateurs du fichier...")
    for data in utilisateurs:
        if Utilisateur.objects.filter(username=data['username']).exists():
            Utilisateur.objects.get(username=data['username']).delete()
            print(f"🔄 Ancien utilisateur {data['username']} supprimé")
        creer_utilisateur(data)
    lister_utilisateurs()


def synchroniser_utilisateurs():
    """
    Synchronise la base avec la liste `utilisateurs`.
    - supprime les utilisateurs absents du fichier
    - met à jour ceux présents
    - crée ceux manquants
    """
    print("\n🔄 Synchronisation complète avec le fichier...")

    usernames_fichier = {u['username'] for u in utilisateurs}

    # 1. Supprimer les utilisateurs absents du fichier
    for user in Utilisateur.objects.all():
        if user.username not in usernames_fichier:
            print(f"🗑️  Supprimé de la base (absent du fichier) : {user.username}")
            user.delete()

    # 2. Créer ou mettre à jour ceux du fichier
    for data in utilisateurs:
        if Utilisateur.objects.filter(username=data['username']).exists():
            mettre_a_jour_utilisateur(data)
        else:
            creer_utilisateur(data)

    lister_utilisateurs()


def main():
    print("=" * 60)
    print("🔧 Gestion des utilisateurs - Plateforme FCP")
    print("=" * 60)

    print("\nQue voulez-vous faire ?")
    print("1 - Créer les nouveaux utilisateurs")
    print("2 - Supprimer un utilisateur")
    print("3 - Lister tous les utilisateurs")
    print("4 - Recréer tous les utilisateurs du fichier")
    print("5 - Synchroniser la base avec le fichier")

    choix = input("\nVotre choix (1-5) : ").strip()

    if choix == '1':
        print("\n📝 Création des nouveaux utilisateurs...")
        total = 0
        success = 0
        for utilisateur in utilisateurs:
            total += 1
            if creer_utilisateur(utilisateur):
                success += 1
        print(f"\n📊 Résumé : {success}/{total} utilisateurs créés")
        lister_utilisateurs()

    elif choix == '2':
        username = input("Nom d'utilisateur à supprimer : ").strip()
        supprimer_utilisateur(username)
        lister_utilisateurs()

    elif choix == '3':
        lister_utilisateurs()

    elif choix == '4':
        recreer_tous_les_utilisateurs()

    elif choix == '5':
        synchroniser_utilisateurs()

    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()