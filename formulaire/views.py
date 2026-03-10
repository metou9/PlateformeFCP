from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import logout
from functools import wraps

from .models import SousProjet, Wilaya, Moughataa, Commune, Utilisateur
from .forms import (
    SousProjetForm, InfrastructureFormSet, EquipementFormSet,
    IntrantFormSet, RealisationFormSet, EmpruntFormSet
)
from .auth_forms import LoginForm  # On garde seulement LoginForm

# ============================================
# DÉCORATEUR POUR PROTÉGER LES VUES
# ============================================

def login_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est connecté"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('formulaire:login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# VUES D'AUTHENTIFICATION (CONNEXION UNIQUEMENT)
# ============================================

def login_view(request):
    """Page de connexion"""
    # Si déjà connecté, rediriger vers l'accueil
    if request.session.get('user_id'):
        return redirect('formulaire:accueil')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                utilisateur = Utilisateur.objects.get(username=username)
                if utilisateur.check_password(password) and utilisateur.actif:
                    # Connexion réussie
                    request.session['user_id'] = utilisateur.id
                    request.session['user_name'] = f"{utilisateur.prenom} {utilisateur.nom}"
                    request.session['user_role'] = utilisateur.role
                    
                    # Mettre à jour la date de dernier login
                    utilisateur.dernier_login = timezone.now()
                    utilisateur.save()
                    
                    messages.success(request, f"Bienvenue {utilisateur.prenom}!")
                    return redirect('formulaire:accueil')
                else:
                    messages.error(request, "Mot de passe incorrect ou compte inactif")
            except Utilisateur.DoesNotExist:
                messages.error(request, "Nom d'utilisateur inexistant")
    else:
        form = LoginForm()
    
    return render(request, 'formulaire/login.html', {'form': form})

def logout_view(request):
    """Déconnexion"""
    logout(request)
    request.session.flush()
    messages.success(request, "Vous avez été déconnecté")
    return redirect('formulaire:login')

# ============================================
# VUES PROTÉGÉES DE L'APPLICATION
# ============================================

@login_required
def accueil(request):
    """Page d'accueil après connexion"""
    from django.utils import timezone
    import datetime
    
    # Statistiques
    total_projets = SousProjet.objects.count()
    en_attente = SousProjet.objects.filter(statut='en_attente').count() if hasattr(SousProjet, 'statut') else 0
    derniers_projets = SousProjet.objects.all().order_by('-date_creation')[:5]
    
    context = {
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        'total_projets': total_projets,
        'en_attente': en_attente,
        'derniers_projets': derniers_projets,
        'now': timezone.now(),
    }
    return render(request, 'formulaire/accueil.html', context)

@login_required
def nouveau_sous_projet(request):
    print("\n" + "="*60)
    print("🔍 NOUVELLE REQUÊTE SUR /formulaire/nouveau/")
    print(f"📌 Méthode: {request.method}")
    print(f"👤 Utilisateur: {request.session.get('user_name')}")
    print("="*60)
    
    if request.method == 'POST':
        # Crée une copie modifiable des données POST
        post_data = request.POST.copy()
        
        # AFFICHE LES DONNÉES REÇUES
        print("\n📦 DONNÉES POST REÇUES:")
        print("-" * 40)
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                print(f"  {key}: {value}")
        print("-" * 40)
        
        # CORRECTION: Vérifie et corrige les IDs
        # Moughataa
        moughataa_id = post_data.get('moughataa')
        if moughataa_id and moughataa_id.isdigit():
            if not Moughataa.objects.filter(id=moughataa_id).exists():
                print(f"⚠️ Moughataa ID {moughataa_id} n'existe pas, recherche d'une alternative...")
                # Cherche la première moughataa de la wilaya sélectionnée
                wilaya_id = post_data.get('wilaya')
                if wilaya_id and wilaya_id.isdigit():
                    premiere_moughataa = Moughataa.objects.filter(wilaya_id=wilaya_id).first()
                    if premiere_moughataa:
                        post_data['moughataa'] = str(premiere_moughataa.id)
                        print(f"✅ Moughataa corrigée à {premiere_moughataa.id} ({premiere_moughataa.nom})")
        
        # Commune
        commune_id = post_data.get('commune')
        if commune_id and commune_id.isdigit():
            if not Commune.objects.filter(id=commune_id).exists():
                print(f"⚠️ Commune ID {commune_id} n'existe pas, recherche d'une alternative...")
                # Cherche la première commune de la moughataa sélectionnée
                moughataa_id = post_data.get('moughataa')
                if moughataa_id and moughataa_id.isdigit():
                    premiere_commune = Commune.objects.filter(moughataa_id=moughataa_id).first()
                    if premiere_commune:
                        post_data['commune'] = str(premiere_commune.id)
                        print(f"✅ Commune corrigée à {premiere_commune.id} ({premiere_commune.nom})")
        
        print("\n📦 DONNÉES POST CORRIGÉES:")
        print("-" * 40)
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                print(f"  {key}: {value}")
        print("-" * 40)
        
        # Initialisation des formulaires avec les données corrigées
        print("\n🔄 Initialisation des formulaires...")
        form = SousProjetForm(post_data)
        infrastructure_formset = InfrastructureFormSet(post_data, prefix='infra')
        equipement_formset = EquipementFormSet(post_data, prefix='equip')
        intrant_formset = IntrantFormSet(post_data, prefix='intrant')
        realisation_formset = RealisationFormSet(post_data, prefix='real')
        emprunt_formset = EmpruntFormSet(post_data, prefix='emprunt')
        
        # Validation individuelle
        print("\n🔍 VALIDATION DES FORMULAIRES:")
        print("-" * 40)
        
        # Formulaire principal
        print(f"📋 Formulaire principal:")
        print(f"  - Valide: {form.is_valid()}")
        if not form.is_valid():
            print(f"  - Erreurs: {form.errors}")
            for field, errors in form.errors.items():
                print(f"    • {field}: {', '.join(errors)}")
        
        # Infrastructure
        print(f"\n🏗️ Infrastructure FormSet:")
        print(f"  - Valide: {infrastructure_formset.is_valid()}")
        if not infrastructure_formset.is_valid():
            print(f"  - Erreurs: {infrastructure_formset.errors}")
        
        # Équipement
        print(f"\n🔧 Equipement FormSet:")
        print(f"  - Valide: {equipement_formset.is_valid()}")
        if not equipement_formset.is_valid():
            print(f"  - Erreurs: {equipement_formset.errors}")
        
        # Intrants
        print(f"\n🌾 Intrant FormSet:")
        print(f"  - Valide: {intrant_formset.is_valid()}")
        if not intrant_formset.is_valid():
            print(f"  - Erreurs: {intrant_formset.errors}")
        
        # Réalisations
        print(f"\n📊 Realisation FormSet:")
        print(f"  - Valide: {realisation_formset.is_valid()}")
        if not realisation_formset.is_valid():
            print(f"  - Erreurs: {realisation_formset.errors}")
        else:
            print(f"  - Nombre de formulaires: {len(realisation_formset.forms)}")
            for i, rform in enumerate(realisation_formset.forms):
                if rform.cleaned_data:
                    print(f"    • Réalisation {i+1}: {rform.cleaned_data}")
        
        # Emprunts
        print(f"\n💰 Emprunt FormSet:")
        print(f"  - Valide: {emprunt_formset.is_valid()}")
        if not emprunt_formset.is_valid():
            print(f"  - Erreurs: {emprunt_formset.errors}")
        else:
            print(f"  - Nombre de formulaires: {len(emprunt_formset.forms)}")
            for i, eform in enumerate(emprunt_formset.forms):
                if eform.cleaned_data:
                    print(f"    • Emprunt {i+1}: {eform.cleaned_data}")
        
        # Validation globale
        all_valid = all([
            form.is_valid(),
            infrastructure_formset.is_valid(),
            equipement_formset.is_valid(),
            intrant_formset.is_valid(),
            realisation_formset.is_valid(),
            emprunt_formset.is_valid()
        ])
        
        print("\n" + "="*40)
        print(f"✅ Tous les formulaires sont valides: {all_valid}")
        print("="*40)
        
        if all_valid:
            try:
                # Sauvegarde du sous-projet principal
                print("\n💾 Sauvegarde du sous-projet principal...")
                sous_projet = form.save()
                print(f"  ✅ Sous-projet créé avec ID: {sous_projet.id}")
                
                # Sauvegarde des infrastructures
                print("\n🏗️ Sauvegarde des infrastructures...")
                infrastructure_formset.instance = sous_projet
                infra_saved = infrastructure_formset.save()
                print(f"  ✅ {len(infra_saved)} infrastructures sauvegardées")
                
                # Sauvegarde des équipements
                print("\n🔧 Sauvegarde des équipements...")
                equipement_formset.instance = sous_projet
                equip_saved = equipement_formset.save()
                print(f"  ✅ {len(equip_saved)} équipements sauvegardés")
                
                # Sauvegarde des intrants
                print("\n🌾 Sauvegarde des intrants...")
                intrant_formset.instance = sous_projet
                intrant_saved = intrant_formset.save()
                print(f"  ✅ {len(intrant_saved)} intrants sauvegardés")
                
                # Sauvegarde des réalisations
                print("\n📊 Sauvegarde des réalisations...")
                real_count = 0
                for real_form in realisation_formset:
                    if real_form.cleaned_data and real_form.cleaned_data.get('annee'):
                        realisation = real_form.save(commit=False)
                        realisation.sous_projet = sous_projet
                        realisation.save()
                        real_count += 1
                        print(f"  ✅ Réalisation {real_count} sauvegardée")
                
                # Sauvegarde des emprunts
                print("\n💰 Sauvegarde des emprunts...")
                emp_count = 0
                for emp_form in emprunt_formset:
                    if emp_form.cleaned_data and emp_form.cleaned_data.get('annee'):
                        emprunt = emp_form.save(commit=False)
                        emprunt.sous_projet = sous_projet
                        emprunt.save()
                        emp_count += 1
                        print(f"  ✅ Emprunt {emp_count} sauvegardé")
                
                print("\n" + "="*40)
                print("🎉 TOUTES LES DONNÉES ONT ÉTÉ SAUVEGARDÉES AVEC SUCCÈS!")
                print("="*40)
                
                messages.success(request, '✅ Sous-projet enregistré avec succès!')
                return redirect('formulaire:liste_sous_projets')
                
            except Exception as e:
                print(f"\n❌ ERREUR LORS DE LA SAUVEGARDE: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, f'Erreur lors de la sauvegarde: {e}')
        else:
            print("\n❌ LE FORMULAIRE N'EST PAS VALIDE - RECHERCHE DES ERREURS:")
            
            # Analyse détaillée des erreurs
            if not form.is_valid():
                print("\n  📋 Erreurs formulaire principal:")
                for field, errors in form.errors.items():
                    print(f"    - {field}: {', '.join(errors)}")
            
            if not infrastructure_formset.is_valid():
                print("\n  🏗️ Erreurs Infrastructure FormSet:")
                for i, errors in enumerate(infrastructure_formset.errors):
                    if errors:
                        print(f"    - Ligne {i+1}: {errors}")
            
            if not equipement_formset.is_valid():
                print("\n  🔧 Erreurs Equipement FormSet:")
                for i, errors in enumerate(equipement_formset.errors):
                    if errors:
                        print(f"    - Ligne {i+1}: {errors}")
            
            if not intrant_formset.is_valid():
                print("\n  🌾 Erreurs Intrant FormSet:")
                for i, errors in enumerate(intrant_formset.errors):
                    if errors:
                        print(f"    - Ligne {i+1}: {errors}")
            
            if not realisation_formset.is_valid():
                print("\n  📊 Erreurs Realisation FormSet:")
                for i, errors in enumerate(realisation_formset.errors):
                    if errors:
                        print(f"    - Ligne {i+1}: {errors}")
            
            if not emprunt_formset.is_valid():
                print("\n  💰 Erreurs Emprunt FormSet:")
                for i, errors in enumerate(emprunt_formset.errors):
                    if errors:
                        print(f"    - Ligne {i+1}: {errors}")
    
    else:
        print("\n📋 AFFICHAGE DU FORMULAIRE VIDE")
        # Formulaire vide
        form = SousProjetForm()
        infrastructure_formset = InfrastructureFormSet(prefix='infra')
        equipement_formset = EquipementFormSet(prefix='equip')
        intrant_formset = IntrantFormSet(prefix='intrant')
        realisation_formset = RealisationFormSet(prefix='real')
        emprunt_formset = EmpruntFormSet(prefix='emprunt')
    
    context = {
        'form': form,
        'infrastructure_formset': infrastructure_formset,
        'equipement_formset': equipement_formset,
        'intrant_formset': intrant_formset,
        'realisation_formset': realisation_formset,
        'emprunt_formset': emprunt_formset,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
    }
    return render(request, 'formulaire/nouveau_sous_projet.html', context)

@login_required
def liste_sous_projets(request):
    sous_projets = SousProjet.objects.all().order_by('-date_creation')
    print(f"\n📋 Liste des sous-projets: {sous_projets.count()} trouvés")
    return render(request, 'formulaire/liste_sous_projets.html', {
        'sous_projets': sous_projets,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
    })

@login_required
def detail_sous_projet(request, pk):
    sous_projet = get_object_or_404(SousProjet, pk=pk)
    print(f"\n🔍 Détail du sous-projet ID: {pk}")
    return render(request, 'formulaire/detail_sous_projet.html', {
        'sous_projet': sous_projet,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
    })

# ============================================
# API NON PROTÉGÉES (accessibles sans authentification)
# ============================================

def get_moughataas(request):
    wilaya_id = request.GET.get('wilaya_id')
    print(f"\n📍 API get_moughataas - wilaya_id: {wilaya_id}")
    
    if wilaya_id:
        moughataas = Moughataa.objects.filter(wilaya_id=wilaya_id).order_by('nom')
        print(f"  📌 {moughataas.count()} moughataas trouvées")
        data = [{'id': m.id, 'nom': m.nom} for m in moughataas]
        return JsonResponse(data, safe=False)
    
    print("  ⚠️ Aucun wilaya_id fourni")
    return JsonResponse([], safe=False)

def get_communes(request):
    moughataa_id = request.GET.get('moughataa_id')
    print(f"\n📍 API get_communes - moughataa_id: {moughataa_id}")
    
    if moughataa_id and moughataa_id.isdigit():
        try:
            communes = Commune.objects.filter(moughataa_id=moughataa_id).order_by('nom')
            print(f"  📍 {communes.count()} communes trouvées")
            data = [{'id': c.id, 'nom': c.nom} for c in communes]
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    print("  ⚠️ Aucun ID valide fourni")
    return JsonResponse([], safe=False)