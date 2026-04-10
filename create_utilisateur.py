#!/usr/bin/env python3
"""
Script pour insérer des utilisateurs dans la table formulaire_utilisateur
Utilisation: python create_utilisateur.py
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialiser Django
django.setup()

from django.contrib.auth.hashers import make_password
from formulaire.models import Utilisateur, Wilaya

# Liste des utilisateurs à insérer
utilisateurs = [
    {
        'nom': 'Isselmou',
        'prenom': 'Iss',
        'username': 'admin1',
        'password': 'admin12',
        'role': 'admin',
        'email': 'mamadou.diallo@fcp.com',
        'actif': True,
        'wilaya_code': None
    },
    {
        'nom': 'Diop',
        'prenom': 'Aissatou',
        'username': 'adiop',
        'password': 'adiop123',
        'role': 'agent',
        'email': 'aissatou.diop@fcp.com',
        'actif': True,
        'wilaya_code': 'Gorgol'
    },
    {
        'nom': 'Sow',
        'prenom': 'Oumar',
        'username': 'osow',
        'password': 'osow123',
        'role': 'agent',
        'email': 'oumar.sow@fcp.com',
        'actif': True,
        'wilaya_code': 'Assaba'
    },
    {
        'nom': 'Ba',
        'prenom': 'Fatou',
        'username': 'fba',
        'password': 'fba123',
        'role': 'agent',
        'email': 'fatou.ba@fcp.com',
        'actif': True,
        'wilaya_code': 'Brakna'
    },
    {
        'nom': 'Ndiaye',
        'prenom': 'Modou',
        'username': 'mndiaye',
        'password': 'mndiaye123',
        'role': 'agent',
        'email': 'modou.ndiaye@fcp.com',
        'actif': True,
        'wilaya_code': 'Trarza'
    },
    {
        'nom': 'Sy',
        'prenom': 'Aminata',
        'username': 'asy',
        'password': 'asy123',
        'role': 'superviseur',
        'email': 'aminata.sy@fcp.com',
        'actif': True,
        'wilaya_code': None
    },
    {
        'nom': 'Faye',
        'prenom': 'Ibrahima',
        'username': 'ifaye',
        'password': 'ifaye123',
        'role': 'consultant',
        'email': 'ibrahima.faye@fcp.com',
        'actif': True,
        'wilaya_code': None
    }
]

def creer_utilisateur(data):
    """Crée un utilisateur dans la base de données"""
    try:
        # Vérifier si l'utilisateur existe déjà
        if Utilisateur.objects.filter(username=data['username']).exists():
            print(f"⚠️  L'utilisateur {data['username']} existe déjà - Ignoré")
            return False
        
        # Créer l'utilisateur avec la méthode set_password qui hash automatiquement
        wilaya = None
        wilaya_code = data.get('wilaya_code')
        if wilaya_code:
            wilaya = Wilaya.objects.filter(code=wilaya_code).first()
            if not wilaya:
                print(f"⚠️  Wilaya introuvable pour le code {wilaya_code} - utilisateur non créé")
                return False

        utilisateur = Utilisateur(
            nom=data['nom'],
            prenom=data['prenom'],
            username=data['username'],
            email=data['email'],
            role=data['role'],
            wilaya=wilaya,
            actif=data.get('actif', True)
        )
        
        # Utiliser la méthode set_password pour hasher le mot de passe
        utilisateur.set_password(data['password'])
        utilisateur.save()
        
        print(f"✅ Utilisateur créé : {utilisateur.username} - {utilisateur.prenom} {utilisateur.nom} ({utilisateur.role}) - Wilaya: {utilisateur.wilaya.nom if utilisateur.wilaya else 'Aucune'}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur pour {data['username']} : {str(e)}")
        return False

def supprimer_utilisateur(username):
    """Supprime un utilisateur"""
    try:
        user = Utilisateur.objects.get(username=username)
        user.delete()
        print(f"🗑️  Utilisateur supprimé : {username}")
        return True
    except Utilisateur.DoesNotExist:
        print(f"⚠️  Utilisateur {username} non trouvé")
        return False

def lister_utilisateurs():
    """Affiche tous les utilisateurs"""
    print("\n" + "="*60)
    print("Liste des utilisateurs dans la base :")
    print("="*60)
    for user in Utilisateur.objects.all():
        print(f"  • {user.username} : {user.prenom} {user.nom} - {user.get_role_display()} - {'Actif' if user.actif else 'Inactif'}")
    print("="*60)

def main():
    print("="*60)
    print("🔧 Gestion des utilisateurs - Plateforme FCP")
    print("="*60)
    
    # Demander l'action à l'utilisateur
    print("\nQue voulez-vous faire ?")
    print("1 - Créer de nouveaux utilisateurs")
    print("2 - Supprimer un utilisateur")
    print("3 - Lister tous les utilisateurs")
    print("4 - Tout créer (ignorer les existants)")
    
    choix = input("\nVotre choix (1-4) : ").strip()
    
    if choix == '1':
        print("\n📝 Création des utilisateurs...")
        total = 0
        success = 0
        for utilisateur in utilisateurs:
            total += 1
            if creer_utilisateur(utilisateur):
                success += 1
        print(f"\n📊 Résumé : {success}/{total} utilisateurs créés")
        lister_utilisateurs()
        
    elif choix == '2':
        username = input("Nom d'utilisateur à supprimer : ")
        supprimer_utilisateur(username)
        lister_utilisateurs()
        
    elif choix == '3':
        lister_utilisateurs()
        
    elif choix == '4':
        print("\n📝 Création forcée de tous les utilisateurs...")
        for utilisateur in utilisateurs:
            # Supprimer si existe
            if Utilisateur.objects.filter(username=utilisateur['username']).exists():
                Utilisateur.objects.get(username=utilisateur['username']).delete()
                print(f"🔄 Ancien utilisateur {utilisateur['username']} supprimé")
            creer_utilisateur(utilisateur)
        lister_utilisateurs()
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()