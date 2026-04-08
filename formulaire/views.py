"""
formulaire/views.py
Vues de l'application FCP
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import logout
from functools import wraps

from .models import (
    SousProjet, Wilaya, Moughataa, Commune, Paysage, Village, 
    Utilisateur, Infrastructure, Equipement, Intrant, 
    Fonctionnement, Service, RealisationPassee, PassifEmprunt
)
from .forms import (
    SousProjetForm, InfrastructureFormSet, EquipementFormSet,
    IntrantFormSet, FonctionnementFormSet, ServiceFormSet,
    ActiviteFormSet,
    RealisationFormSet, EmpruntFormSet
)
from .auth_forms import LoginForm


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def clean_formset_data(post_data, prefix):
    """
    Supprime les formulaires vides d'un formset
    """
    total_forms = int(post_data.get(f'{prefix}-TOTAL_FORMS', 0))
    for i in range(total_forms - 1, -1, -1):
        has_data = False
        for key, value in post_data.items():
            if key.startswith(f'{prefix}-{i}-') and value:
                has_data = True
                break
        if not has_data:
            keys_to_del = [k for k in post_data.keys() if k.startswith(f'{prefix}-{i}-')]
            for key in keys_to_del:
                del post_data[key]
            post_data[f'{prefix}-TOTAL_FORMS'] = str(total_forms - 1)
            total_forms -= 1
    return post_data


def get_current_sous_projet(request):
    """
    Récupère le sous-projet en cours de création depuis la session
    """
    sous_projet_id = request.session.get('current_sous_projet_id')
    if sous_projet_id:
        try:
            return SousProjet.objects.get(id=sous_projet_id)
        except SousProjet.DoesNotExist:
            return None
    return None


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


def detail_sous_projet(request, pk):
    """Affiche le détail d'un sous-projet spécifique avec calcul des montants"""
    sous_projet = get_object_or_404(SousProjet, pk=pk)
    
    # ============================================
    # Calcul pour INFRASTRUCTURES (Prix unitaire × Quantité)
    # ============================================
    infrastructures = []
    total_infra = 0
    for infra in sous_projet.infrastructures.all():
        quantite = infra.quantite or 0
        prix_unit = infra.prix_unit or 0
        montant_calcule = quantite * prix_unit
        total_infra += montant_calcule
        
        infrastructures.append({
            'id': infra.id,
            'description': infra.description,
            'quantite': quantite,
            'prix_unit': prix_unit,
            'montant_total': montant_calcule,
            'subvention_padisam': infra.subvention_padisam,
            'contribution_promoteur': infra.contribution_promoteur,
            'autre_financement': infra.autre_financement,
        })
    
    # ============================================
    # Calcul pour EQUIPEMENTS (Prix unitaire × Quantité)
    # ============================================
    equipements = []
    total_equip = 0
    for equip in sous_projet.equipements.all():
        quantite = equip.quantite or 0
        prix_unit = equip.prix_unit or 0
        montant_calcule = quantite * prix_unit
        total_equip += montant_calcule
        
        equipements.append({
            'id': equip.id,
            'description': equip.description,
            'quantite': quantite,
            'prix_unit': prix_unit,
            'montant_total': montant_calcule,
            'subvention_padisam': equip.subvention_padisam,
            'contribution_promoteur': equip.contribution_promoteur,
            'autre_financement': equip.autre_financement,
        })
    
    # ============================================
    # Calcul pour INTRANTS (Prix unitaire × Quantité)
    # ============================================
    intrants = []
    total_intrant = 0
    for intrant in sous_projet.intrants.all():
        quantite = intrant.quantite or 0
        prix_unit = intrant.prix_unit or 0
        montant_calcule = quantite * prix_unit
        total_intrant += montant_calcule
        
        intrants.append({
            'id': intrant.id,
            'description': intrant.description,
            'quantite': quantite,
            'prix_unit': prix_unit,
            'montant_total': montant_calcule,
            'subvention_padisam': intrant.subvention_padisam,
            'contribution_promoteur': intrant.contribution_promoteur,
            'autre_financement': intrant.autre_financement,
        })
    
    # ============================================
    # Calcul pour FONCTIONNEMENT (Prix unitaire × Quantité)
    # ============================================
    fonctionnements = []
    total_fonc = 0
    for fonc in sous_projet.fonctionnements.all():
        quantite = fonc.quantite or 0
        prix_unit = fonc.prix_unit or 0
        montant_calcule = quantite * prix_unit
        total_fonc += montant_calcule
        
        fonctionnements.append({
            'id': fonc.id,
            'description': fonc.description,
            'quantite': quantite,
            'prix_unit': prix_unit,
            'montant_total': montant_calcule,
            'contribution_promoteur': fonc.contribution_promoteur,
            'autre_financement': fonc.autre_financement,
        })
    
    # ============================================
    # Calcul pour SERVICES (Prix unitaire × Quantité)
    # ============================================
    services = []
    total_serv = 0
    for serv in sous_projet.services.all():
        quantite = serv.quantite or 0
        prix_unit = serv.prix_unit or 0
        montant_calcule = quantite * prix_unit
        total_serv += montant_calcule
        
        services.append({
            'id': serv.id,
            'description': serv.description,
            'quantite': quantite,
            'prix_unit': prix_unit,
            'montant_total': montant_calcule,
            'subvention_padisam': serv.subvention_padisam,
            'contribution_promoteur': serv.contribution_promoteur,
            'autre_financement': serv.autre_financement,
        })
    
    # Grand total de tous les financements
    grand_total = total_infra + total_equip + total_intrant + total_fonc + total_serv
    
    # Totaux des ventes
    total_ventes = sum(real.ventes_usd or 0 for real in sous_projet.realisations.all())
    
    # Totaux des emprunts
    total_emprunte = sum(emp.montant_emprunte or 0 for emp in sous_projet.emprunts.all())
    total_rembourse = sum(emp.montant_rembourse or 0 for emp in sous_projet.emprunts.all())
    
    context = {
        'sous_projet': sous_projet,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        # Infrastructures
        'infrastructures': infrastructures,
        'total_infra': total_infra,
        # Équipements
        'equipements': equipements,
        'total_equip': total_equip,
        # Intrants
        'intrants': intrants,
        'total_intrant': total_intrant,
        # Fonctionnements
        'fonctionnements': fonctionnements,
        'total_fonc': total_fonc,
        # Services
        'services': services,
        'total_serv': total_serv,
        # Grand total
        'grand_total': grand_total,
        # Ventes et emprunts
        'total_ventes': total_ventes,
        'total_emprunte': total_emprunte,
        'total_rembourse': total_rembourse,
    }
    return render(request, 'formulaire/detail_sous_projet.html', context)

# ============================================
# VUES D'AUTHENTIFICATION
# ============================================

def login_view(request):
    """Page de connexion"""
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
                    request.session['user_id'] = utilisateur.id
                    request.session['user_name'] = f"{utilisateur.prenom} {utilisateur.nom}"
                    request.session['user_role'] = utilisateur.role
                    
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
    total_projets = SousProjet.objects.count()
    derniers_projets = SousProjet.objects.all().order_by('-date_creation')[:5]
    
    context = {
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        'total_projets': total_projets,
        'derniers_projets': derniers_projets,
        'now': timezone.now(),
    }
    return render(request, 'formulaire/accueil.html', context)


# ============================================
# ÉTAPE 1: INFORMATIONS GÉNÉRALES
# ============================================

@login_required
def nouveau_sous_projet(request):
    """Étape 1: Formulaire des informations générales"""
    if request.method == 'POST':
        form = SousProjetForm(request.POST)
        if form.is_valid():
            sous_projet = form.save()
            request.session['current_sous_projet_id'] = sous_projet.id
            messages.success(request, '✅ Informations générales enregistrées')
            return redirect('formulaire:financement_infrastructure')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field}: {error}")
    else:
        # Récupérer les données de session si elles existent
        sous_projet = get_current_sous_projet(request)
        if sous_projet:
            form = SousProjetForm(instance=sous_projet)
        else:
            form = SousProjetForm()
    
    return render(request, 'formulaire/nv_sous_projet.html', {'form': form})


@login_required
def save_sous_projet(request):
    """Sauvegarde de l'étape 1"""
    return nouveau_sous_projet(request)


# ============================================
# ÉTAPE 2: INFRASTRUCTURES
# ============================================

@login_required
def financement_infrastructure(request):
    """Étape 2: Gestion des infrastructures"""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')
    
    if request.method == 'POST':
        formset = InfrastructureFormSet(request.POST, instance=sous_projet, prefix='infra')
        if formset.is_valid():
            formset.save()
            messages.success(request, '✅ Infrastructures enregistrées')
            return redirect('formulaire:financement_equipement')
        else:
            for form in formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Infrastructure - {field}: {error}")
    else:
        formset = InfrastructureFormSet(instance=sous_projet, prefix='infra')
    
    return render(request, 'formulaire/financement_infrastructure.html', {
        'infrastructure_formset': formset,
        'sous_projet': sous_projet
    })


@login_required
def save_infrastructure(request):
    """Sauvegarde de l'étape 2"""
    return financement_infrastructure(request)

def nv_sous_projet(request):
    """Étape 1: Formulaire des informations générales"""
    if request.method == 'POST':
        form = SousProjetForm(request.POST)
        activite_formset = ActiviteFormSet(request.POST, prefix='activite')
        
        if form.is_valid() and activite_formset.is_valid():
            sous_projet = form.save()
            activite_formset.instance = sous_projet
            activite_formset.save()
            request.session['current_sous_projet_id'] = sous_projet.id
            messages.success(request, '✅ Informations générales enregistrées')
            return redirect('formulaire:financement_infrastructure')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field}: {error}")
    else:
        sous_projet = get_current_sous_projet(request)
        if sous_projet:
            form = SousProjetForm(instance=sous_projet)
            activite_formset = ActiviteFormSet(instance=sous_projet, prefix='activite')
        else:
            form = SousProjetForm()
            activite_formset = ActiviteFormSet(prefix='activite')
    
    return render(request, 'formulaire/nv_sous_projet.html', {
        'form': form,
        'activite_formset': activite_formset,
        'sous_projet': sous_projet
    })


# ============================================
# ÉTAPE 3: ÉQUIPEMENTS
# ============================================

@login_required
def financement_equipement(request):
    """Étape 3: Gestion des équipements"""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')
    
    if request.method == 'POST':
        formset = EquipementFormSet(request.POST, instance=sous_projet, prefix='equip')
        if formset.is_valid():
            formset.save()
            messages.success(request, '✅ Équipements enregistrés')
            return redirect('formulaire:financement_intrant')
        else:
            for form in formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Équipement - {field}: {error}")
    else:
        formset = EquipementFormSet(instance=sous_projet, prefix='equip')
    
    return render(request, 'formulaire/financement_equipement.html', {
        'equipement_formset': formset,
        'sous_projet': sous_projet
    })


@login_required
def save_equipement(request):
    """Sauvegarde de l'étape 3"""
    return financement_equipement(request)


# ============================================
# ÉTAPE 4: INTRANTS
# ============================================

@login_required
def financement_intrant(request):
    """Étape 4: Gestion des intrants"""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')
    
    if request.method == 'POST':
        formset = IntrantFormSet(request.POST, instance=sous_projet, prefix='intrant')
        if formset.is_valid():
            formset.save()
            messages.success(request, '✅ Intrants enregistrés')
            return redirect('formulaire:financement_fonctionnement')
        else:
            for form in formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Intrant - {field}: {error}")
    else:
        formset = IntrantFormSet(instance=sous_projet, prefix='intrant')
    
    return render(request, 'formulaire/financement_intrant.html', {
        'intrant_formset': formset,
        'sous_projet': sous_projet
    })


@login_required
def save_intrant(request):
    """Sauvegarde de l'étape 4"""
    return financement_intrant(request)


# ============================================
# ÉTAPE 5: FONCTIONNEMENT
# ============================================

@login_required
def financement_fonctionnement(request):
    """Étape 5: Gestion du fonctionnement"""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')
    
    if request.method == 'POST':
        formset = FonctionnementFormSet(request.POST, instance=sous_projet, prefix='fonc')
        if formset.is_valid():
            formset.save()
            messages.success(request, '✅ Fonctionnement enregistré')
            return redirect('formulaire:financement_services')
        else:
            for form in formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Fonctionnement - {field}: {error}")
    else:
        formset = FonctionnementFormSet(instance=sous_projet, prefix='fonc')
    
    return render(request, 'formulaire/financement_fonctionnement.html', {
        'fonctionnement_formset': formset,
        'sous_projet': sous_projet
    })


@login_required
def save_fonctionnement(request):
    """Sauvegarde de l'étape 5"""
    return financement_fonctionnement(request)


# ============================================
# ÉTAPE 6: SERVICES
# ============================================

@login_required
def financement_services(request):
    """Étape 6: Gestion des services"""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')
    
    if request.method == 'POST':
        formset = ServiceFormSet(request.POST, instance=sous_projet, prefix='serv')
        if formset.is_valid():
            formset.save()
            messages.success(request, '✅ Services enregistrés')
            return redirect('formulaire:realisation_passif')
        else:
            for form in formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Service - {field}: {error}")
    else:
        formset = ServiceFormSet(instance=sous_projet, prefix='serv')
    
    return render(request, 'formulaire/financement_services.html', {
        'service_formset': formset,
        'sous_projet': sous_projet
    })


@login_required
def save_service(request):
    """Sauvegarde de l'étape 6"""
    return financement_services(request)


# ============================================
# ÉTAPE 7: RÉALISATIONS ET EMPRUNTS
# ============================================

@login_required
def realisation_passif(request):
    """Étape 7: Gestion des réalisations et emprunts"""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')
    
    if request.method == 'POST':
        realisation_formset = RealisationFormSet(request.POST, prefix='real')
        emprunt_formset = EmpruntFormSet(request.POST, prefix='emprunt')
        
        if realisation_formset.is_valid() and emprunt_formset.is_valid():
            # Sauvegarde des réalisations
            for real_form in realisation_formset.forms:
                if real_form.cleaned_data and real_form.cleaned_data.get('annee'):
                    realisation = real_form.save(commit=False)
                    realisation.sous_projet = sous_projet
                    realisation.save()
            
            # Sauvegarde des emprunts
            for emp_form in emprunt_formset.forms:
                if emp_form.cleaned_data and emp_form.cleaned_data.get('annee'):
                    emprunt = emp_form.save(commit=False)
                    emprunt.sous_projet = sous_projet
                    emprunt.save()
            
            # Nettoyer la session
            del request.session['current_sous_projet_id']
            
            messages.success(request, '✅ Sous-projet créé avec succès!')
            return redirect('formulaire:liste_sous_projets')
        else:
            for form in realisation_formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Réalisation - {field}: {error}")
            for form in emprunt_formset.forms:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ Emprunt - {field}: {error}")
    else:
        realisation_formset = RealisationFormSet(prefix='real')
        emprunt_formset = EmpruntFormSet(prefix='emprunt')
    
    return render(request, 'formulaire/realisation_passif.html', {
        'realisation_formset': realisation_formset,
        'emprunt_formset': emprunt_formset,
        'sous_projet': sous_projet
    })


@login_required
def save_realisation_passif(request):
    """Sauvegarde de l'étape 7"""
    return realisation_passif(request)


# ============================================
# LISTE ET DÉTAIL
# ============================================

@login_required
def liste_sous_projets(request):
    """Affiche la liste de tous les sous-projets"""
    sous_projets = SousProjet.objects.all().order_by('-date_creation')
    return render(request, 'formulaire/liste_sous_projets.html', {
        'sous_projets': sous_projets,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
    })


@login_required
def detail_sous_projet(request, pk):
    """Affiche le détail d'un sous-projet spécifique"""
    sous_projet = get_object_or_404(SousProjet, pk=pk)
    return render(request, 'formulaire/detail_sous_projet.html', {
        'sous_projet': sous_projet,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
    })

@login_required
def supprimer_sous_projet(request, pk):
    """Supprime un sous-projet spécifique"""
    sous_projet = get_object_or_404(SousProjet, pk=pk)
    
    if request.method == 'POST':
        intitule = sous_projet.intitule_sous_projet
        sous_projet.delete()
        messages.success(request, f'✅ Sous-projet "{intitule}" supprimé avec succès!')
        return redirect('formulaire:liste_sous_projets')
    
    return redirect('formulaire:liste_sous_projets')

# ============================================
# API NON PROTÉGÉES
# ============================================

def get_moughataas(request):
    """API: Récupère les moughataas d'une wilaya donnée"""
    wilaya_id = request.GET.get('wilaya_id')
    if wilaya_id:
        moughataas = Moughataa.objects.filter(wilaya_id=wilaya_id).order_by('nom')
        data = [{'id': m.id, 'nom': m.nom} for m in moughataas]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_communes(request):
    """API: Récupère les communes d'une moughataa donnée"""
    moughataa_id = request.GET.get('moughataa_id')
    if moughataa_id and moughataa_id.isdigit():
        try:
            communes = Commune.objects.filter(moughataa_id=moughataa_id).order_by('nom')
            data = [{'id': c.id, 'nom': c.nom} for c in communes]
            return JsonResponse(data, safe=False)
        except Exception:
            return JsonResponse([], safe=False)
    return JsonResponse([], safe=False)


def get_paysages(request):
    """API: Récupère les paysages d'une commune donnée"""
    commune_id = request.GET.get('commune_id')
    if commune_id and commune_id.isdigit():
        try:
            paysages = Paysage.objects.filter(commune_id=commune_id).order_by('nom')
            data = [{'id': p.id, 'nom': p.nom} for p in paysages]
            return JsonResponse(data, safe=False)
        except Exception:
            return JsonResponse([], safe=False)
    return JsonResponse([], safe=False)


def get_villages(request):
    """API: Récupère les villages d'un paysage donné"""
    paysage_id = request.GET.get('paysage_id')
    if paysage_id and paysage_id.isdigit():
        try:
            villages = Village.objects.filter(paysage_id=paysage_id).order_by('nom')
            data = [{'nom': v.nom} for v in villages]
            return JsonResponse(data, safe=False)
        except Exception:
            return JsonResponse([], safe=False)
    return JsonResponse([], safe=False)