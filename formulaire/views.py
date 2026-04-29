"""
formulaire/views.py
Vues principales de l'application FCP / PADISAM
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Count
from django.contrib.auth.decorators import login_required


from .auth_forms import LoginForm
from .forms import (
    SousProjetForm,
    InfrastructureFormSet,
    EquipementFormSet,
    PromoteurFinalForm,
    IntrantFormSet,
    FonctionnementFormSet,
    ServiceFormSet,
    RealisationFormSet,
    EmpruntFormSet,
    ResultatPreselectionFormSet, 
    DecisionComiteSousProjetForm
)
from .models import (
    SousProjet,
    ResultatPreselection,
    Wilaya,
    Moughataa,
    Commune,
    Paysage,
    Village,
    Utilisateur,
    Infrastructure,
    Equipement,
    Intrant,
    Fonctionnement,
    Service,
    Activite,
    RealisationPassee,
    PassifEmprunt,
)


# =========================================================
# OUTILS GÉNÉRAUX
# =========================================================

def get_current_user(request):
    """Récupère l'utilisateur connecté à partir de la session."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None

    try:
        return Utilisateur.objects.select_related('wilaya').get(id=user_id, actif=True)
    except Utilisateur.DoesNotExist:
        return None


def is_agent_saisie(utilisateur):
    """Retourne True si l'utilisateur est un agent de saisie."""
    return bool(utilisateur and utilisateur.role == 'agent')
def is_superadmin(utilisateur):
    return bool(utilisateur and utilisateur.role == 'superadmin')


def is_admin(utilisateur):
    return bool(utilisateur and utilisateur.role == 'admin')


def is_admin_like(utilisateur):
    """
    Admin-like = admin + superadmin
    """
    return bool(utilisateur and utilisateur.role in ['admin', 'superadmin'])


def is_comite(utilisateur):
    """
    Accès comité = prescomite + superadmin
    """
    return bool(utilisateur and utilisateur.role in ['prescomite', 'superadmin'])


def can_delete_projects(utilisateur):
    return is_admin_like(utilisateur)


def can_manage_all_projects(utilisateur):
    return is_admin_like(utilisateur)


def can_validate_comite(utilisateur):
    return bool(utilisateur and utilisateur.role in ['prescomite', 'superadmin'])

def can_view_comite_list(utilisateur):
    return bool(utilisateur and utilisateur.role in [
        'admin', 'agent', 'superviseur', 'superadmin', 'prescomite'
    ])

def get_accessible_sous_projets(utilisateur):
    """
    Sous-projets visibles selon le rôle.
    - admin et superadmin : voient tous les sous-projets
    - autres utilisateurs avec wilaya : voient seulement les sous-projets de leur wilaya
    - utilisateur sans wilaya et non admin : ne voit rien
    """
    if not utilisateur:
        return SousProjet.objects.none()

    if can_manage_all_projects(utilisateur):
        return SousProjet.objects.all()

    if utilisateur.wilaya_id:
        return SousProjet.objects.filter(wilaya_id=utilisateur.wilaya_id)

    return SousProjet.objects.none()

def get_current_sous_projet(request):
    """
    Récupère le sous-projet en cours depuis la session.
    Si le sous-projet n'est plus accessible, on nettoie la session.
    """
    sous_projet_id = request.session.get('current_sous_projet_id')
    utilisateur = get_current_user(request)

    if sous_projet_id and utilisateur:
        try:
            return get_accessible_sous_projets(utilisateur).get(id=sous_projet_id)
        except SousProjet.DoesNotExist:
            request.session.pop('current_sous_projet_id', None)
            return None

    return None


def login_required(view_func):
    """Décorateur de protection des vues."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('formulaire:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# =========================================================
# OUTILS DE TOTALS FINANCEMENT
# =========================================================

def compute_financement_totals(queryset, include_subvention=True):
    """
    Calcule les totaux d'une section de financement.
    """
    if include_subvention:
        totals = queryset.aggregate(
            total_montant=Sum('montant_total'),
            total_subvention=Sum('subvention_padisam'),
            total_contribution=Sum('contribution_promoteur'),
            total_autre=Sum('autre_financement'),
        )
        return {
            'total_montant': totals['total_montant'] or 0,
            'total_subvention': totals['total_subvention'] or 0,
            'total_contribution': totals['total_contribution'] or 0,
            'total_autre': totals['total_autre'] or 0,
        }

    totals = queryset.aggregate(
        total_montant=Sum('montant_total'),
        total_contribution=Sum('contribution_promoteur'),
        total_autre=Sum('autre_financement'),
    )
    return {
        'total_montant': totals['total_montant'] or 0,
        'total_contribution': totals['total_contribution'] or 0,
        'total_autre': totals['total_autre'] or 0,
    }


# =========================================================
# FABRIQUES DE FORMSETS DYNAMIQUES
# =========================================================
# IMPORTANT :
# On garde les widgets/styles définis dans forms.py.
# On ne recrée PAS les formsets de financement à la main.
# On clone seulement la classe et on ajuste `extra`.

def clone_formset_with_extra(base_formset_class, extra_value):
    """
    Clone un formset existant en conservant ses widgets et options,
    puis remplace simplement la propriété extra.
    """
    CustomFormSet = type(
        f"Custom{base_formset_class.__name__}",
        (base_formset_class,),
        {'extra': extra_value}
    )
    return CustomFormSet


def get_activite_formset_class(extra=0):
    """
    Formset dynamique pour les activités.
    Ici on garde le formulaire custom ActiviteForm.
    """
    from .forms import ActiviteForm, BaseActiviteFormSet
    return inlineformset_factory(
        SousProjet,
        Activite,
        form=ActiviteForm,
        extra=extra,
        can_delete=True,
        formset=BaseActiviteFormSet
    )


# =========================================================
# AUTHENTIFICATION
# =========================================================

def login_view(request):
    """Page de connexion."""
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
                    request.session['user_wilaya_id'] = utilisateur.wilaya_id
                    request.session['user_wilaya_nom'] = utilisateur.wilaya.nom if utilisateur.wilaya else ''

                    utilisateur.dernier_login = timezone.now()
                    utilisateur.save()

                    messages.success(request, f"Bienvenue {utilisateur.prenom} !")
                    return redirect('formulaire:accueil')
                else:
                    messages.error(request, "Mot de passe incorrect ou compte inactif.")

            except Utilisateur.DoesNotExist:
                messages.error(request, "Nom d'utilisateur inexistant.")
    else:
        form = LoginForm()

    return render(request, 'formulaire/login.html', {'form': form})


def logout_view(request):
    """Déconnexion."""
    logout(request)
    request.session.flush()
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('formulaire:login')


# =========================================================
# ACCUEIL
# =========================================================

@login_required
def accueil(request):
    """Page d'accueil."""
    utilisateur = get_current_user(request)
    sous_projets = get_accessible_sous_projets(utilisateur)

    mode_label = ""
    wilaya_label = ""

    if utilisateur:
        if utilisateur.role == 'superadmin':
            mode_label = "Super administrateur"
        elif utilisateur.role == 'admin':
            mode_label = "Administrateur"
        elif utilisateur.role == 'agent':
            mode_label = "Saisie"
        elif utilisateur.role == 'prescomite':
            mode_label = "Président du comité de présélection"
        elif utilisateur.role == 'superviseur':
            mode_label = "Superviseur"
        elif utilisateur.role == 'consultant':
            mode_label = "Consultant"
        else:
            mode_label = utilisateur.role

        if utilisateur.role not in ['admin', 'superadmin'] and utilisateur.wilaya:
            wilaya_label = utilisateur.wilaya.nom

    context = {
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        'user_wilaya_nom': request.session.get('user_wilaya_nom'),
        'mode_label': mode_label,
        'wilaya_label': wilaya_label,
        'total_projets': sous_projets.count(),
        'derniers_projets': sous_projets.order_by('-date_creation')[:5],
        'now': timezone.now(),
    }
    return render(request, 'formulaire/accueil.html', context)
# =========================================================
# ÉTAPE 1 : INFORMATIONS GÉNÉRALES + ACTIVITÉS
# =========================================================


@login_required
def nouveau_sous_projet(request):
    """
    Étape 1 :
    - formulaire principal
    - activités

    Règle :
    - nouveau dossier : 1 ligne activité
    - refresh / dossier existant : pas de ligne vide supplémentaire
    """
    utilisateur = get_current_user(request)
    sous_projet = get_current_sous_projet(request)

    if utilisateur and utilisateur.role == 'prescomite':
        messages.error(request, "❌ Le président du comité de présélection n'est pas autorisé à créer un nouveau dossier.")
        return redirect('formulaire:accueil')

    if is_agent_saisie(utilisateur) and not utilisateur.wilaya_id:
        messages.error(request, "Cet agent n'a pas de wilaya affectée. Impossible de créer un sous-projet.")
        return redirect('formulaire:accueil')

    if request.method == 'POST':
        form = SousProjetForm(request.POST, instance=sous_projet, user=utilisateur)

        ActiviteDynamicFormSet = get_activite_formset_class(extra=0)
        activite_formset = ActiviteDynamicFormSet(
            request.POST,
            instance=sous_projet if sous_projet else SousProjet(),
            prefix='activite'
        )

        if form.is_valid() and activite_formset.is_valid():
            sous_projet = form.save(commit=False)

            if is_agent_saisie(utilisateur):
                sous_projet.wilaya = utilisateur.wilaya

            # Ajouter le username du créateur
            if utilisateur:
                sous_projet.createur_username = utilisateur.username

            sous_projet.save()

            activite_formset.instance = sous_projet
            activite_formset.save()

            request.session['current_sous_projet_id'] = sous_projet.id
            messages.success(request, "✅ Informations générales enregistrées.")
            return redirect('formulaire:financement_infrastructure')

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"❌ {field} : {error}")

        if activite_formset.non_form_errors():
            for error in activite_formset.non_form_errors():
                messages.error(request, f"❌ Activités : {error}")

    else:
        form = SousProjetForm(instance=sous_projet, user=utilisateur) if sous_projet else SousProjetForm(user=utilisateur)

        if sous_projet and sous_projet.pk and sous_projet.activites.exists():
            ActiviteDynamicFormSet = get_activite_formset_class(extra=0)
        else:
            ActiviteDynamicFormSet = get_activite_formset_class(extra=1)

        activite_formset = ActiviteDynamicFormSet(
            instance=sous_projet if sous_projet else SousProjet(),
            prefix='activite'
        )

    return render(request, 'formulaire/nv_sous_projet.html', {
        'form': form,
        'activite_formset_data': activite_formset,
        'sous_projet': sous_projet,
        'user_wilaya_nom': request.session.get('user_wilaya_nom'),
    })


@login_required
def save_sous_projet(request):
    """Alias de sauvegarde étape 1."""
    return nouveau_sous_projet(request)


@login_required
def statistiques(request):
    utilisateur = get_current_user(request)
    sous_projets = get_accessible_sous_projets(utilisateur)

    total_projets = sous_projets.count()

    # 1) Totaux par wilaya
    stats_wilayas = (
        sous_projets
        .values('wilaya__nom')
        .annotate(total=Count('id'))
        .order_by('wilaya__nom')
    )

    # 2) Détail Paysage / ZOCA par wilaya
    stats_paysages = (
        sous_projets
        .values('wilaya__nom', 'paysage__nom')
        .annotate(total=Count('id'))
        .order_by('wilaya__nom', 'paysage__nom')
    )

    stats_wilaya_paysages = []
    for wilaya in stats_wilayas:
        wilaya_nom = wilaya['wilaya__nom'] or "Non renseignée"

        paysages = []
        for item in stats_paysages:
            item_wilaya = item['wilaya__nom'] or "Non renseignée"
            if item_wilaya == wilaya_nom:
                paysages.append({
                    'paysage': item['paysage__nom'] or "Non renseigné",
                    'total': item['total'],
                })

        stats_wilaya_paysages.append({
            'wilaya': wilaya_nom,
            'total': wilaya['total'],
            'paysages': paysages,
        })

    # 3) Types de projet avec pourcentage
    stats_types_raw = (
        sous_projets
        .values('type_projet')
        .annotate(total=Count('id'))
        .order_by('type_projet')
    )

    type_map = {
        'AG': 'Agriculture',
        'EL': 'Élevage',
        'ENV': 'Environnement',
    }

    stats_types = []
    chart_labels = []
    chart_data = []

    for item in stats_types_raw:
        code = item['type_projet'] or "NR"
        label = type_map.get(code, code)
        total = item['total']
        pourcentage = round((total / total_projets) * 100, 2) if total_projets else 0

        stats_types.append({
            'type': label,
            'total': total,
            'pourcentage': pourcentage,
        })
        stats_agents = (
             sous_projets
             .values('createur_username')
             .annotate(total=Count('id'))
             .order_by('-total', 'createur_username')
        )

        chart_labels.append(label)
        chart_data.append(pourcentage)

    context = {
        'total_projets': total_projets,
        'stats_wilaya_paysages': stats_wilaya_paysages,
        'stats_types': stats_types,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'stats_agents': stats_agents,
    }

    return render(request, 'formulaire/statistiques.html', context)
# =========================================================
# ÉTAPE 2 : INFRASTRUCTURES
# =========================================================

@login_required
def financement_infrastructure(request):
    """
    Étape 2 :
    - premier affichage : 3 lignes vides
    - refresh / données existantes : 0 ligne vide supplémentaire
    """
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')

    DynamicInfrastructureFormSet = clone_formset_with_extra(
        InfrastructureFormSet,
        0 if sous_projet.infrastructures.exists() else 3
    )

    if request.method == 'POST':
        formset = DynamicInfrastructureFormSet(request.POST, instance=sous_projet, prefix='infra')
        if formset.is_valid():
            formset.save()
            messages.success(request, "✅ Infrastructures enregistrées.")
            return redirect('formulaire:financement_equipement')

        for form in formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Infrastructure - {field} : {error}")
    else:
        formset = DynamicInfrastructureFormSet(instance=sous_projet, prefix='infra')

    infrastructures_totaux = compute_financement_totals(
        sous_projet.infrastructures.all(),
        include_subvention=True
    )

    return render(request, 'formulaire/financement_infrastructure.html', {
        'infrastructure_formset': formset,
        'sous_projet': sous_projet,
        'infrastructures_totaux': infrastructures_totaux,
    })


@login_required
def save_infrastructure(request):
    return financement_infrastructure(request)


# =========================================================
# ÉTAPE 3 : ÉQUIPEMENTS
# =========================================================

@login_required
def financement_equipement(request):
    """
    Étape 3 :
    - premier affichage : 3 lignes vides
    - refresh / données existantes : 0 ligne vide supplémentaire
    """
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')

    DynamicEquipementFormSet = clone_formset_with_extra(
        EquipementFormSet,
        0 if sous_projet.equipements.exists() else 3
    )

    if request.method == 'POST':
        formset = DynamicEquipementFormSet(request.POST, instance=sous_projet, prefix='equip')
        if formset.is_valid():
            formset.save()
            messages.success(request, "✅ Équipements enregistrés.")
            return redirect('formulaire:financement_intrant')

        for form in formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Équipement - {field} : {error}")
    else:
        formset = DynamicEquipementFormSet(instance=sous_projet, prefix='equip')

    equipements_totaux = compute_financement_totals(
        sous_projet.equipements.all(),
        include_subvention=True
    )

    return render(request, 'formulaire/financement_equipement.html', {
        'equipement_formset': formset,
        'sous_projet': sous_projet,
        'equipements_totaux': equipements_totaux,
    })


@login_required
def save_equipement(request):
    return financement_equipement(request)


# =========================================================
# ÉTAPE 4 : INTRANTS
# =========================================================

@login_required
def financement_intrant(request):
    """
    Étape 4 :
    - premier affichage : 3 lignes vides
    - refresh / données existantes : 0 ligne vide supplémentaire
    """
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')

    DynamicIntrantFormSet = clone_formset_with_extra(
        IntrantFormSet,
        0 if sous_projet.intrants.exists() else 3
    )

    if request.method == 'POST':
        formset = DynamicIntrantFormSet(request.POST, instance=sous_projet, prefix='intrant')
        if formset.is_valid():
            formset.save()
            messages.success(request, "✅ Intrants enregistrés.")
            return redirect('formulaire:financement_fonctionnement')

        for form in formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Intrant - {field} : {error}")
    else:
        formset = DynamicIntrantFormSet(instance=sous_projet, prefix='intrant')

    intrants_totaux = compute_financement_totals(
        sous_projet.intrants.all(),
        include_subvention=True
    )

    return render(request, 'formulaire/financement_intrant.html', {
        'intrant_formset': formset,
        'sous_projet': sous_projet,
        'intrants_totaux': intrants_totaux,
    })


@login_required
def save_intrant(request):
    return financement_intrant(request)


# =========================================================
# ÉTAPE 5 : FONCTIONNEMENT
# =========================================================

@login_required
def financement_fonctionnement(request):
    """
    Étape 5 :
    - premier affichage : 1 ligne vide
    - refresh / données existantes : 0 ligne vide supplémentaire
    """
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')

    DynamicFonctionnementFormSet = clone_formset_with_extra(
        FonctionnementFormSet,
        0 if sous_projet.fonctionnements.exists() else 1
    )

    if request.method == 'POST':
        formset = DynamicFonctionnementFormSet(request.POST, instance=sous_projet, prefix='fonc')
        if formset.is_valid():
            formset.save()
            messages.success(request, "✅ Fonctionnement enregistré.")
            return redirect('formulaire:financement_services')

        for form in formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Fonctionnement - {field} : {error}")
    else:
        formset = DynamicFonctionnementFormSet(instance=sous_projet, prefix='fonc')

    fonctionnements_totaux = compute_financement_totals(
        sous_projet.fonctionnements.all(),
        include_subvention=False
    )

    return render(request, 'formulaire/financement_fonctionnement.html', {
        'fonctionnement_formset': formset,
        'sous_projet': sous_projet,
        'fonctionnements_totaux': fonctionnements_totaux,
    })


@login_required
def save_fonctionnement(request):
    return financement_fonctionnement(request)


# =========================================================
# ÉTAPE 6 : SERVICES
# =========================================================

@login_required
def financement_services(request):
    """
    Étape 6 :
    - premier affichage : 1 ligne vide
    - refresh / données existantes : 0 ligne vide supplémentaire
    """
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')

    DynamicServiceFormSet = clone_formset_with_extra(
        ServiceFormSet,
        0 if sous_projet.services.exists() else 1
    )

    if request.method == 'POST':
        formset = DynamicServiceFormSet(request.POST, instance=sous_projet, prefix='serv')
        if formset.is_valid():
            formset.save()
            messages.success(request, "✅ Services enregistrés.")
            return redirect('formulaire:realisation_passif')

        for form in formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Service - {field} : {error}")
    else:
        formset = DynamicServiceFormSet(instance=sous_projet, prefix='serv')

    services_totaux = compute_financement_totals(
        sous_projet.services.all(),
        include_subvention=True
    )

    return render(request, 'formulaire/financement_services.html', {
        'service_formset': formset,
        'sous_projet': sous_projet,
        'services_totaux': services_totaux,
    })


@login_required
def save_service(request):
    return financement_services(request)


# =========================================================
# ÉTAPE 7 : RÉALISATIONS PASSÉES ET EMPRUNTS
# =========================================================

@login_required
def realisation_passif(request):
    """Étape 7 : informations finales, réalisations passées et emprunts."""
    sous_projet = get_current_sous_projet(request)
    if not sous_projet:
        return redirect('formulaire:nouveau_sous_projet')

    if request.method == 'POST':
        promoteur_form = PromoteurFinalForm(request.POST, instance=sous_projet)
        realisation_formset = RealisationFormSet(request.POST, prefix='real')
        emprunt_formset = EmpruntFormSet(request.POST, prefix='emprunt')

        if promoteur_form.is_valid() and realisation_formset.is_valid() and emprunt_formset.is_valid():
            promoteur_form.save()

            # On remplace complètement les anciennes réalisations
            sous_projet.realisations.all().delete()

            for real_form in realisation_formset:
                cleaned_data = getattr(real_form, 'cleaned_data', None)
                if not cleaned_data:
                    continue

                produit = cleaned_data.get('produit')

                annee_1 = cleaned_data.get('annee_1')
                volume_1 = cleaned_data.get('volume_annee_1')
                ventes_1 = cleaned_data.get('ventes_usd_annee_1')
                prix_1 = cleaned_data.get('prix_vente_mru_annee_1')

                annee_2 = cleaned_data.get('annee_2')
                volume_2 = cleaned_data.get('volume_annee_2')
                ventes_2 = cleaned_data.get('ventes_usd_annee_2')
                prix_2 = cleaned_data.get('prix_vente_mru_annee_2')

                annee_3 = cleaned_data.get('annee_3')
                volume_3 = cleaned_data.get('volume_annee_3')
                ventes_3 = cleaned_data.get('ventes_usd_annee_3')
                prix_3 = cleaned_data.get('prix_vente_mru_annee_3')

                has_data = any([
                    produit,
                    annee_1, volume_1, ventes_1, prix_1,
                    annee_2, volume_2, ventes_2, prix_2,
                    annee_3, volume_3, ventes_3, prix_3,
                ])

                if not has_data:
                    continue

                RealisationPassee.objects.create(
                    sous_projet=sous_projet,
                    produit=produit,

                    annee_1=annee_1,
                    volume_annee_1=volume_1,
                    ventes_usd_annee_1=ventes_1,
                    prix_vente_mru_annee_1=prix_1,

                    annee_2=annee_2,
                    volume_annee_2=volume_2,
                    ventes_usd_annee_2=ventes_2,
                    prix_vente_mru_annee_2=prix_2,

                    annee_3=annee_3,
                    volume_annee_3=volume_3,
                    ventes_usd_annee_3=ventes_3,
                    prix_vente_mru_annee_3=prix_3,
                )

            # On remplace complètement les anciens emprunts
            sous_projet.emprunts.all().delete()

            for emp_form in emprunt_formset:
                cleaned_data = getattr(emp_form, 'cleaned_data', None)
                if not cleaned_data:
                    continue

                annee = cleaned_data.get('annee')
                institution = cleaned_data.get('institution_financiere')
                montant_emprunte = cleaned_data.get('montant_emprunte')
                montant_rembourse = cleaned_data.get('montant_rembourse')

                has_data = any([
                    annee,
                    institution,
                    montant_emprunte,
                    montant_rembourse,
                ])

                if not has_data:
                    continue

                PassifEmprunt.objects.create(
                    sous_projet=sous_projet,
                    annee=annee,
                    institution_financiere=institution,
                    montant_emprunte=montant_emprunte,
                    montant_rembourse=montant_rembourse,
                )

            request.session.pop('current_sous_projet_id', None)
            messages.success(request, "✅ Sous-projet créé avec succès !")
            return redirect('formulaire:liste_sous_projets')

        for field, errors in promoteur_form.errors.items():
            for error in errors:
                messages.error(request, f"❌ Promoteur - {field} : {error}")

        for form in realisation_formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Réalisation - {field} : {error}")

        for form in emprunt_formset.forms:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Emprunt - {field} : {error}")

    else:
        promoteur_form = PromoteurFinalForm(instance=sous_projet)

        realisations_initial = [
            {
                'produit': r.produit,

                'annee_1': r.annee_1,
                'volume_annee_1': r.volume_annee_1,
                'ventes_usd_annee_1': r.ventes_usd_annee_1,
                'prix_vente_mru_annee_1': r.prix_vente_mru_annee_1,

                'annee_2': r.annee_2,
                'volume_annee_2': r.volume_annee_2,
                'ventes_usd_annee_2': r.ventes_usd_annee_2,
                'prix_vente_mru_annee_2': r.prix_vente_mru_annee_2,

                'annee_3': r.annee_3,
                'volume_annee_3': r.volume_annee_3,
                'ventes_usd_annee_3': r.ventes_usd_annee_3,
                'prix_vente_mru_annee_3': r.prix_vente_mru_annee_3,
            }
            for r in sous_projet.realisations.all()
        ]

        emprunts_initial = [
            {
                'annee': e.annee,
                'institution_financiere': e.institution_financiere,
                'montant_emprunte': e.montant_emprunte,
                'montant_rembourse': e.montant_rembourse,
            }
            for e in sous_projet.emprunts.all()
        ]

        realisation_formset = RealisationFormSet(
            prefix='real',
            initial=realisations_initial
        )
        emprunt_formset = EmpruntFormSet(
            prefix='emprunt',
            initial=emprunts_initial
        )

    return render(request, 'formulaire/realisation_passif.html', {
        'promoteur_form': promoteur_form,
        'realisation_formset': realisation_formset,
        'emprunt_formset': emprunt_formset,
        'sous_projet': sous_projet,
    })


@login_required
def save_realisation_passif(request):
    return realisation_passif(request)


# =========================================================
# LISTE / DÉTAIL / SUPPRESSION
# =========================================================

@login_required
def liste_sous_projets(request):
    """Liste des sous-projets accessibles."""
    utilisateur = get_current_user(request)
    sous_projets = get_accessible_sous_projets(utilisateur).order_by('-date_creation')

    return render(request, 'formulaire/liste_sous_projets.html', {
        'sous_projets': sous_projets,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        'user_wilaya_nom': request.session.get('user_wilaya_nom'),
        'is_admin': is_admin_like(utilisateur),
        'is_superadmin': is_superadmin(utilisateur),
    })

@login_required
def detail_sous_projet(request, pk):
    """Détail d'un sous-projet."""
    utilisateur = get_current_user(request)
    sous_projet = get_object_or_404(get_accessible_sous_projets(utilisateur), pk=pk)

    infrastructures = list(sous_projet.infrastructures.all())
    equipements = list(sous_projet.equipements.all())
    intrants = list(sous_projet.intrants.all())
    fonctionnements = list(sous_projet.fonctionnements.all())
    services = list(sous_projet.services.all())

    total_infrastructures = sous_projet.infrastructures.aggregate(total=Sum('montant_total'))['total'] or 0
    total_equipements = sous_projet.equipements.aggregate(total=Sum('montant_total'))['total'] or 0
    total_intrants = sous_projet.intrants.aggregate(total=Sum('montant_total'))['total'] or 0
    total_fonctionnements = sous_projet.fonctionnements.aggregate(total=Sum('montant_total'))['total'] or 0
    total_services = sous_projet.services.aggregate(total=Sum('montant_total'))['total'] or 0

    # Totaux détaillés par source de financement
    infra_subvention = sous_projet.infrastructures.aggregate(total=Sum('subvention_padisam'))['total'] or 0
    infra_contribution = sous_projet.infrastructures.aggregate(total=Sum('contribution_promoteur'))['total'] or 0
    infra_autre = sous_projet.infrastructures.aggregate(total=Sum('autre_financement'))['total'] or 0

    equip_subvention = sous_projet.equipements.aggregate(total=Sum('subvention_padisam'))['total'] or 0
    equip_contribution = sous_projet.equipements.aggregate(total=Sum('contribution_promoteur'))['total'] or 0
    equip_autre = sous_projet.equipements.aggregate(total=Sum('autre_financement'))['total'] or 0

    intrant_subvention = sous_projet.intrants.aggregate(total=Sum('subvention_padisam'))['total'] or 0
    intrant_contribution = sous_projet.intrants.aggregate(total=Sum('contribution_promoteur'))['total'] or 0
    intrant_autre = sous_projet.intrants.aggregate(total=Sum('autre_financement'))['total'] or 0

    fonct_contribution = sous_projet.fonctionnements.aggregate(total=Sum('contribution_promoteur'))['total'] or 0
    fonct_autre = sous_projet.fonctionnements.aggregate(total=Sum('autre_financement'))['total'] or 0

    service_subvention = sous_projet.services.aggregate(total=Sum('subvention_padisam'))['total'] or 0
    service_contribution = sous_projet.services.aggregate(total=Sum('contribution_promoteur'))['total'] or 0
    service_autre = sous_projet.services.aggregate(total=Sum('autre_financement'))['total'] or 0

    grand_total = (
        total_infrastructures +
        total_equipements +
        total_intrants +
        total_fonctionnements +
        total_services
    )

    total_ventes = 0
    for real in sous_projet.realisations.all():
        total_ventes += (real.ventes_usd_annee_1 or 0)
        total_ventes += (real.ventes_usd_annee_2 or 0)
        total_ventes += (real.ventes_usd_annee_3 or 0)

    total_emprunte = sum(emp.montant_emprunte or 0 for emp in sous_projet.emprunts.all())
    total_rembourse = sum(emp.montant_rembourse or 0 for emp in sous_projet.emprunts.all())

    context = {
        'sous_projet': sous_projet,
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        'user_wilaya_nom': request.session.get('user_wilaya_nom'),

        'infrastructures': infrastructures,
        'equipements': equipements,
        'intrants': intrants,
        'fonctionnements': fonctionnements,
        'services': services,

        'total_infrastructures': total_infrastructures,
        'total_equipements': total_equipements,
        'total_intrants': total_intrants,
        'total_fonctionnements': total_fonctionnements,
        'total_services': total_services,

        'infra_subvention': infra_subvention,
        'infra_contribution': infra_contribution,
        'infra_autre': infra_autre,

        'equip_subvention': equip_subvention,
        'equip_contribution': equip_contribution,
        'equip_autre': equip_autre,

        'intrant_subvention': intrant_subvention,
        'intrant_contribution': intrant_contribution,
        'intrant_autre': intrant_autre,

        'fonct_contribution': fonct_contribution,
        'fonct_autre': fonct_autre,

        'service_subvention': service_subvention,
        'service_contribution': service_contribution,
        'service_autre': service_autre,

        'grand_total': grand_total,
        'total_ventes': total_ventes,
        'total_emprunte': total_emprunte,
        'total_rembourse': total_rembourse,
    }

    return render(request, 'formulaire/detail_sous_projet.html', context)
@login_required
def supprimer_sous_projet(request, pk):
    """Supprime un sous-projet accessible."""
    utilisateur = get_current_user(request)

    if not can_delete_projects(utilisateur):
        messages.error(request, "❌ Seuls les administrateurs peuvent supprimer un sous-projet.")
        return redirect('formulaire:liste_sous_projets')

    sous_projet = get_object_or_404(get_accessible_sous_projets(utilisateur), pk=pk)

    if request.method == 'POST':
        intitule = sous_projet.intitule_sous_projet
        sous_projet.delete()
        messages.success(request, f'✅ Sous-projet "{intitule}" supprimé avec succès !')
        return redirect('formulaire:liste_sous_projets')

    return redirect('formulaire:liste_sous_projets')
# =========================================================
# API AJAX
# =========================================================

def get_moughataas(request):
    """Retourne les moughataas d'une wilaya."""
    wilaya_id = request.GET.get('wilaya_id')
    user_role = request.session.get('user_role')
    user_wilaya_id = request.session.get('user_wilaya_id')

    if user_role == 'agent' and user_wilaya_id and str(wilaya_id) != str(user_wilaya_id):
        return JsonResponse([], safe=False)

    if wilaya_id:
        moughataas = Moughataa.objects.filter(wilaya_id=wilaya_id).order_by('nom')
        data = [{'id': m.id, 'nom': m.nom} for m in moughataas]
        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)


def get_communes(request):
    """Retourne les communes d'une moughataa."""
    moughataa_id = request.GET.get('moughataa_id')
    user_role = request.session.get('user_role')
    user_wilaya_id = request.session.get('user_wilaya_id')

    if moughataa_id and moughataa_id.isdigit():
        try:
            communes = Commune.objects.filter(moughataa_id=moughataa_id)

            if user_role == 'agent' and user_wilaya_id:
                communes = communes.filter(moughataa__wilaya_id=user_wilaya_id)

            data = [{'id': c.id, 'nom': c.nom} for c in communes.order_by('nom')]
            return JsonResponse(data, safe=False)
        except Exception:
            return JsonResponse([], safe=False)

    return JsonResponse([], safe=False)


def get_paysages(request):
    """Retourne les paysages d'une commune."""
    commune_id = request.GET.get('commune_id')
    user_role = request.session.get('user_role')
    user_wilaya_id = request.session.get('user_wilaya_id')

    if commune_id and commune_id.isdigit():
        try:
            paysages = Paysage.objects.filter(commune_id=commune_id)

            if user_role == 'agent' and user_wilaya_id:
                paysages = paysages.filter(commune__moughataa__wilaya_id=user_wilaya_id)

            data = [{'id': p.id, 'nom': p.nom} for p in paysages.order_by('nom')]
            return JsonResponse(data, safe=False)
        except Exception:
            return JsonResponse([], safe=False)

    return JsonResponse([], safe=False)


def get_villages(request):
    """Retourne les villages d'un paysage."""
    paysage_id = request.GET.get('paysage_id')

    if paysage_id and paysage_id.isdigit():
        try:
            villages = Village.objects.filter(paysage_id=paysage_id).order_by('nom')
            data = [{'nom': v.nom} for v in villages]
            return JsonResponse(data, safe=False)
        except Exception:
            return JsonResponse([], safe=False)

    return JsonResponse([], safe=False)


def evaluer_preselection(sp):
    """
    Présélection simple de démonstration.
    Règles automatiques vérifiables sur les champs déjà existants.
    """

    criteres = []
    motifs_manquants = []

    # Critères vérifiables
    if sp.numero_reception_formulaire:
        criteres.append("Numéro de réception renseigné")
    else:
        motifs_manquants.append("Numéro de réception non renseigné")

    if sp.intitule_sous_projet:
        criteres.append("Intitulé du sous-projet renseigné")
    else:
        motifs_manquants.append("Intitulé du sous-projet non renseigné")

    if sp.guichet:
        criteres.append("Guichet renseigné")
    else:
        motifs_manquants.append("Guichet non renseigné")

    if sp.type_projet:
        criteres.append("Type de projet renseigné")
    else:
        motifs_manquants.append("Type de projet non renseigné")

    if sp.wilaya:
        criteres.append("Wilaya renseignée")
    else:
        motifs_manquants.append("Wilaya non renseignée")

    if sp.objectif_sous_projet:
        criteres.append("Objectif du sous-projet renseigné")
    else:
        motifs_manquants.append("Objectif du sous-projet non renseigné")

    if sp.nom_statut_juridique:
        criteres.append("Demandeur / bénéficiaire renseigné")
    else:
        motifs_manquants.append("Demandeur / bénéficiaire non renseigné")

    # Décision automatique simple
    if len(motifs_manquants) == 0:
        decision = "Préselectionné"
        motif = "Le dossier contient les informations minimales nécessaires pour passer à l’étape suivante."
        badge_class = "badge-ok"
    elif len(motifs_manquants) <= 2:
        decision = "À examiner"
        motif = "Le dossier est partiellement complet : " + "; ".join(motifs_manquants) + "."
        badge_class = "badge-review"
    else:
        decision = "Rejet provisoire"
        motif = "Le dossier est incomplet : " + "; ".join(motifs_manquants) + "."
        badge_class = "badge-no"

    return {
        "numero_reception": sp.numero_reception_formulaire or "Non renseigné",
        "intitule": sp.intitule_sous_projet or "Non renseigné",
        "critere": " / ".join(criteres) if criteres else "Aucun critère validé",
        "decision": decision,
        "motif": motif,
        "badge_class": badge_class,
        "sous_projet": sp,
    }


@login_required
def preselection_automatique(request):
    """
    Page simple de démonstration de la présélection automatique.
    """
    utilisateur = get_current_user(request)
    sous_projets = get_accessible_sous_projets(utilisateur).order_by("-id")

    lignes = [evaluer_preselection(sp) for sp in sous_projets]

    can_view_preselection_detail = bool(
        utilisateur and utilisateur.role in ['admin', 'superadmin', 'prescomite']
    )

    context = {
        "lignes": lignes,
        "total_dossiers": sous_projets.count(),
        "can_view_preselection_detail": can_view_preselection_detail,
    }
    return render(request, "formulaire/preselection_automatique.html", context)

def evaluer_criteres_preselection(sp):
    """
    Évalue les critères de présélection un par un.
    Si le critère n'est pas mesurable automatiquement avec les données disponibles,
    on met 'À examiner'.
    """
    criteres = []

    def badge_for(decision):
        if decision == "Éligible":
            return "badge-ok"
        if decision == "Non éligible":
            return "badge-no"
        return "badge-review"

    # 1. Zone d’intervention
    if sp.wilaya and sp.commune and sp.paysage:
        criteres.append({
            "numero": 1,
            "critere": "Zone d’intervention",
            "question": "Le sous-projet est-il situé dans une zone couverte par le PADISAM/FCP ?",
            "resultat": "Oui",
            "decision": "Éligible",
            "motif": "Le sous-projet est localisé dans une zone renseignée du projet.",
            "badge_class": badge_for("Éligible"),
        })
    else:
        criteres.append({
            "numero": 1,
            "critere": "Zone d’intervention",
            "question": "Le sous-projet est-il situé dans une zone couverte par le PADISAM/FCP ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "La localisation n’est pas suffisamment renseignée pour confirmer automatiquement la zone.",
            "badge_class": badge_for("À examiner"),
        })

    # 2. Guichet concerné
    if sp.guichet in ["AGR", "ACI"]:
        criteres.append({
            "numero": 2,
            "critere": "Guichet concerné",
            "question": "Le dossier relève-t-il du bon guichet : AGR ou ACI ?",
            "resultat": sp.guichet,
            "decision": "Éligible",
            "motif": "Le guichet est renseigné dans le dossier.",
            "badge_class": badge_for("Éligible"),
        })
    else:
        criteres.append({
            "numero": 2,
            "critere": "Guichet concerné",
            "question": "Le dossier relève-t-il du bon guichet : AGR ou ACI ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "Le guichet n’est pas clairement exploitable automatiquement.",
            "badge_class": badge_for("À examiner"),
        })

    # 3. Profil du promoteur
    if sp.nom_statut_juridique:
        criteres.append({
            "numero": 3,
            "critere": "Profil du promoteur",
            "question": "Le demandeur fait-il partie des catégories admises ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "Le profil exact du promoteur nécessite une lecture métier du statut juridique.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 3,
            "critere": "Profil du promoteur",
            "question": "Le demandeur fait-il partie des catégories admises ?",
            "resultat": "Non renseigné",
            "decision": "À examiner",
            "motif": "Le profil du promoteur n’est pas suffisamment renseigné.",
            "badge_class": badge_for("À examiner"),
        })

    # 4. Statut du promoteur
    if sp.nom_statut_juridique:
        criteres.append({
            "numero": 4,
            "critere": "Statut du promoteur",
            "question": "Le statut du promoteur est-il conforme aux critères d’éligibilité ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "Le statut juridique est renseigné mais nécessite une validation métier.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 4,
            "critere": "Statut du promoteur",
            "question": "Le statut du promoteur est-il conforme aux critères d’éligibilité ?",
            "resultat": "Non renseigné",
            "decision": "À examiner",
            "motif": "Le statut du promoteur n’est pas renseigné.",
            "badge_class": badge_for("À examiner"),
        })

    # 5. Origine du promoteur
    criteres.append({
        "numero": 5,
        "critere": "Origine du promoteur",
        "question": "Le promoteur est-il résident ou originaire de la zone concernée ?",
        "resultat": "À examiner",
        "decision": "À examiner",
        "motif": "Cette information n’est pas disponible de manière fiable dans les champs actuels.",
        "badge_class": badge_for("À examiner"),
    })

    # 6. Dossier complet
    champs_min = [
        sp.numero_reception_formulaire,
        sp.intitule_sous_projet,
        sp.guichet,
        sp.type_projet,
        sp.nom_statut_juridique,
        sp.personne_contact_nom,
        sp.telephone,
        sp.wilaya,
        sp.moughataa,
        sp.commune,
        sp.paysage,
        sp.village,
        sp.objectif_sous_projet,
    ]
    if all(champs_min):
        criteres.append({
            "numero": 6,
            "critere": "Dossier complet",
            "question": "Le formulaire F1 et les pièces exigées sont-ils présents ?",
            "resultat": "Partiellement mesurable",
            "decision": "Éligible",
            "motif": "Les principaux champs du formulaire sont renseignés. Les pièces jointes restent à vérifier.",
            "badge_class": badge_for("Éligible"),
        })
    else:
        criteres.append({
            "numero": 6,
            "critere": "Dossier complet",
            "question": "Le formulaire F1 et les pièces exigées sont-ils présents ?",
            "resultat": "Incomplet",
            "decision": "Non éligible",
            "motif": "Le formulaire contient des informations essentielles manquantes.",
            "badge_class": badge_for("Non éligible"),
        })

    # 7. Activité proposée
    if sp.activites.exists():
        criteres.append({
            "numero": 7,
            "critere": "Activité proposée",
            "question": "L’activité figure-t-elle parmi les activités finançables du FCP ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "Les activités sont renseignées mais leur admissibilité doit être vérifiée selon la grille métier.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 7,
            "critere": "Activité proposée",
            "question": "L’activité figure-t-elle parmi les activités finançables du FCP ?",
            "resultat": "Aucune activité",
            "decision": "Non éligible",
            "motif": "Aucune activité n’est renseignée dans le dossier.",
            "badge_class": badge_for("Non éligible"),
        })

    # 8. Filière / chaîne de valeur
    if sp.chaine_approvisionnement:
        criteres.append({
            "numero": 8,
            "critere": "Filière / chaîne de valeur",
            "question": "Le sous-projet s’inscrit-il dans une filière admissible et prioritaire ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "La chaîne de valeur est renseignée mais doit être confrontée aux priorités de zone.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 8,
            "critere": "Filière / chaîne de valeur",
            "question": "Le sous-projet s’inscrit-il dans une filière admissible et prioritaire ?",
            "resultat": "Non renseigné",
            "decision": "À examiner",
            "motif": "La chaîne de valeur n’est pas renseignée.",
            "badge_class": badge_for("À examiner"),
        })

    # 9. Marché potentiel
    if sp.marches_vises:
        criteres.append({
            "numero": 9,
            "critere": "Marché potentiel",
            "question": "Le marché potentiel est-il identifié et accessible ?",
            "resultat": "Oui, déclaré",
            "decision": "Éligible",
            "motif": "Le dossier identifie un marché ou des débouchés visés.",
            "badge_class": badge_for("Éligible"),
        })
    else:
        criteres.append({
            "numero": 9,
            "critere": "Marché potentiel",
            "question": "Le marché potentiel est-il identifié et accessible ?",
            "resultat": "Non",
            "decision": "À examiner",
            "motif": "Aucun marché visé n’est renseigné.",
            "badge_class": badge_for("À examiner"),
        })

    # 10. Cohérence du sous-projet
    if sp.segment_ca and sp.activites.exists():
        criteres.append({
            "numero": 10,
            "critere": "Cohérence du sous-projet",
            "question": "Le segment de la chaîne de valeur correspond-il au type de sous-projet demandé ?",
            "resultat": "À examiner",
            "decision": "À examiner",
            "motif": "Des données existent mais la cohérence nécessite une lecture métier.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 10,
            "critere": "Cohérence du sous-projet",
            "question": "Le segment de la chaîne de valeur correspond-il au type de sous-projet demandé ?",
            "resultat": "Insuffisant",
            "decision": "À examiner",
            "motif": "Le segment ou les activités ne permettent pas une validation automatique.",
            "badge_class": badge_for("À examiner"),
        })

    # 11. Coûts réalistes
    grand_total = (
        (sp.infrastructures.aggregate(total=Sum('montant_total'))['total'] or 0) +
        (sp.equipements.aggregate(total=Sum('montant_total'))['total'] or 0) +
        (sp.intrants.aggregate(total=Sum('montant_total'))['total'] or 0) +
        (sp.fonctionnements.aggregate(total=Sum('montant_total'))['total'] or 0) +
        (sp.services.aggregate(total=Sum('montant_total'))['total'] or 0)
    )

    if grand_total > 0:
        criteres.append({
            "numero": 11,
            "critere": "Coûts réalistes",
            "question": "Les coûts annoncés sont-ils cohérents avec les barèmes du FCP ?",
            "resultat": f"Total déclaré : {grand_total}",
            "decision": "À examiner",
            "motif": "Les montants existent mais leur conformité aux barèmes doit être vérifiée.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 11,
            "critere": "Coûts réalistes",
            "question": "Les coûts annoncés sont-ils cohérents avec les barèmes du FCP ?",
            "resultat": "Aucun coût exploitable",
            "decision": "À examiner",
            "motif": "Aucun coût consolidé n’est disponible pour une évaluation automatique.",
            "badge_class": badge_for("À examiner"),
        })

    # 12. Plafond de subvention
    total_subvention = (
        (sp.infrastructures.aggregate(total=Sum('subvention_padisam'))['total'] or 0) +
        (sp.equipements.aggregate(total=Sum('subvention_padisam'))['total'] or 0) +
        (sp.intrants.aggregate(total=Sum('subvention_padisam'))['total'] or 0) +
        (sp.services.aggregate(total=Sum('subvention_padisam'))['total'] or 0)
    )

    criteres.append({
        "numero": 12,
        "critere": "Plafond de subvention",
        "question": "La subvention demandée respecte-t-elle le plafond prévu ?",
        "resultat": f"Subvention déclarée : {total_subvention}",
        "decision": "À examiner",
        "motif": "Le montant de subvention doit être comparé aux plafonds par catégorie de promoteur.",
        "badge_class": badge_for("À examiner"),
    })

    # 13. Expérience du promoteur
    if sp.annee_debut_activites:
        criteres.append({
            "numero": 13,
            "critere": "Expérience du promoteur",
            "question": "Le promoteur a-t-il l’ancienneté ou l’expérience minimale requise ?",
            "resultat": f"Début activité : {sp.annee_debut_activites}",
            "decision": "Éligible",
            "motif": "Une ancienneté est renseignée dans le dossier.",
            "badge_class": badge_for("Éligible"),
        })
    else:
        criteres.append({
            "numero": 13,
            "critere": "Expérience du promoteur",
            "question": "Le promoteur a-t-il l’ancienneté ou l’expérience minimale requise ?",
            "resultat": "Non renseigné",
            "decision": "À examiner",
            "motif": "L’ancienneté ou l’expérience n’est pas renseignée.",
            "badge_class": badge_for("À examiner"),
        })

    # 14. Réalisme de l’extension
    if sp.realisations.exists():
        criteres.append({
            "numero": 14,
            "critere": "Réalisme de l’extension",
            "question": "L’augmentation d’activité annoncée est-elle raisonnable ?",
            "resultat": "Historique disponible",
            "decision": "À examiner",
            "motif": "Les réalisations passées existent mais le réalisme de l’extension doit être analysé.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 14,
            "critere": "Réalisme de l’extension",
            "question": "L’augmentation d’activité annoncée est-elle raisonnable ?",
            "resultat": "Pas d’historique",
            "decision": "À examiner",
            "motif": "Aucun historique suffisant pour juger automatiquement l’extension.",
            "badge_class": badge_for("À examiner"),
        })

    # 15. Moyens minimums disponibles
    if sp.ressources_promoteur:
        criteres.append({
            "numero": 15,
            "critere": "Moyens minimums disponibles",
            "question": "Le promoteur dispose-t-il du site, du minimum d’équipement et des ressources techniques de base ?",
            "resultat": "Ressources déclarées",
            "decision": "Éligible",
            "motif": "Des ressources du promoteur sont renseignées dans le dossier.",
            "badge_class": badge_for("Éligible"),
        })
    else:
        criteres.append({
            "numero": 15,
            "critere": "Moyens minimums disponibles",
            "question": "Le promoteur dispose-t-il du site, du minimum d’équipement et des ressources techniques de base ?",
            "resultat": "Non renseigné",
            "decision": "À examiner",
            "motif": "Les moyens minimums ne sont pas décrits dans le dossier.",
            "badge_class": badge_for("À examiner"),
        })

    # 16. Eau / faisabilité du site
    if sp.type_projet == 'AG':
        if sp.ressources_promoteur:
            criteres.append({
                "numero": 16,
                "critere": "Eau / faisabilité du site",
                "question": "Pour un sous-projet agricole, la source d’eau existe-t-elle ?",
                "resultat": "À examiner",
                "decision": "À examiner",
                "motif": "Les ressources sont déclarées mais la disponibilité réelle de l’eau doit être confirmée.",
                "badge_class": badge_for("À examiner"),
            })
        else:
            criteres.append({
                "numero": 16,
                "critere": "Eau / faisabilité du site",
                "question": "Pour un sous-projet agricole, la source d’eau existe-t-elle ?",
                "resultat": "Non renseigné",
                "decision": "À examiner",
                "motif": "Aucune information exploitable sur l’eau n’est disponible.",
                "badge_class": badge_for("À examiner"),
            })
    else:
        criteres.append({
            "numero": 16,
            "critere": "Eau / faisabilité du site",
            "question": "Pour un sous-projet agricole, la source d’eau existe-t-elle ?",
            "resultat": "Non applicable",
            "decision": "Éligible",
            "motif": "Ce critère ne s’applique pas directement à ce type de projet.",
            "badge_class": badge_for("Éligible"),
        })

    # 17. Double financement / duplication
    criteres.append({
        "numero": 17,
        "critere": "Double financement / duplication",
        "question": "Le sous-projet finance-t-il les mêmes dépenses qu’un autre appui déjà obtenu ?",
        "resultat": "À examiner",
        "decision": "À examiner",
        "motif": "Aucune information suffisante dans la base actuelle pour détecter automatiquement une duplication.",
        "badge_class": badge_for("À examiner"),
    })

    # 18. Exigences environnementales et sociales
    criteres.append({
        "numero": 18,
        "critere": "Exigences environnementales et sociales",
        "question": "Le sous-projet respecte-t-il les exigences sociales et environnementales de base ?",
        "resultat": "À examiner",
        "decision": "À examiner",
        "motif": "Le screening E&S n’est pas automatisable avec les champs actuels.",
        "badge_class": badge_for("À examiner"),
    })

    # 19. Antécédents de crédit
    total_rembourse = sum(emp.montant_rembourse or 0 for emp in sp.emprunts.all())
    total_emprunte = sum(emp.montant_emprunte or 0 for emp in sp.emprunts.all())

    if total_emprunte == 0:
        criteres.append({
            "numero": 19,
            "critere": "Antécédents de crédit",
            "question": "Le demandeur a-t-il des antécédents connus de non-remboursement ?",
            "resultat": "Aucun emprunt déclaré",
            "decision": "Éligible",
            "motif": "Aucun antécédent d’emprunt bloquant n’est déclaré.",
            "badge_class": badge_for("Éligible"),
        })
    elif total_rembourse <= total_emprunte:
        criteres.append({
            "numero": 19,
            "critere": "Antécédents de crédit",
            "question": "Le demandeur a-t-il des antécédents connus de non-remboursement ?",
            "resultat": "Données de crédit disponibles",
            "decision": "À examiner",
            "motif": "Les emprunts existent mais l’historique réel de remboursement doit être vérifié qualitativement.",
            "badge_class": badge_for("À examiner"),
        })
    else:
        criteres.append({
            "numero": 19,
            "critere": "Antécédents de crédit",
            "question": "Le demandeur a-t-il des antécédents connus de non-remboursement ?",
            "resultat": "Incohérent",
            "decision": "À examiner",
            "motif": "Les montants d’emprunt et de remboursement sont incohérents et nécessitent vérification.",
            "badge_class": badge_for("À examiner"),
        })

    # 20. Visite de terrain nécessaire
    criteres.append({
        "numero": 20,
        "critere": "Visite de terrain nécessaire",
        "question": "Les informations du dossier suffisent-elles ou une vérification sur site est-elle nécessaire ?",
        "resultat": "Visite recommandée",
        "decision": "À examiner",
        "motif": "Plusieurs critères nécessitent une validation physique ou documentaire complémentaire.",
        "badge_class": badge_for("À examiner"),
    })

    return criteres


@login_required
def preselection_detail(request, pk):
    utilisateur = get_current_user(request)

    if not utilisateur or utilisateur.role not in ['admin', 'superadmin', 'prescomite']:
        messages.error(request, "❌ Vous n'êtes pas autorisé à consulter le détail de la présélection.")
        return redirect('formulaire:preselection_automatique')

    sous_projet = get_object_or_404(get_accessible_sous_projets(utilisateur), pk=pk)

    criteres = evaluer_criteres_preselection(sous_projet)

    nb_eligibles = sum(1 for c in criteres if c['decision'] == 'Éligible')
    nb_non_eligibles = sum(1 for c in criteres if c['decision'] == 'Non éligible')
    nb_a_examiner = sum(1 for c in criteres if c['decision'] == 'À examiner')

    return render(request, 'formulaire/preselection_detail.html', {
        'sous_projet': sous_projet,
        'criteres': criteres,
        'nb_eligibles': nb_eligibles,
        'nb_non_eligibles': nb_non_eligibles,
        'nb_a_examiner': nb_a_examiner,
    })

@login_required
def preselection_comite_liste(request):
    """
    Liste des dossiers pour la présélection comité.
    - admin, agent, superviseur, superadmin, prescomite : peuvent voir la liste
    - seul superadmin et prescomite peuvent valider
    """
    utilisateur = get_current_user(request)

    if not can_view_comite_list(utilisateur):
        messages.error(request, "❌ Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('formulaire:accueil')

    sous_projets = get_accessible_sous_projets(utilisateur).order_by('-id')

    lignes = []
    for sp in sous_projets:
        ligne = evaluer_preselection(sp)

        lignes.append({
            'sous_projet': sp,
            'numero_reception': ligne.get('numero_reception') or "Non renseigné",
            'intitule': ligne.get('intitule') or "Non renseigné",
            'critere': ligne.get('critere'),
            'decision_automatique': ligne.get('decision') or "Non renseigné",
            'motif_automatique': ligne.get('motif') or "Non renseigné",
            'badge_class': ligne.get('badge_class') or "badge-review",
            'decision_comite': sp.decision_comite,
            'motif_comite': sp.motif_comite,
            'status': sp.status,
        })

    context = {
        'lignes': lignes,
        'total_dossiers': sous_projets.count(),
        'can_validate_comite': can_validate_comite(utilisateur),
        'can_view_comite_list': True,
        'is_superadmin': is_superadmin(utilisateur),
    }

    return render(request, 'formulaire/preselection_comite_liste.html', context)

@login_required
def preselection_comite_detail(request, pk):
    """
    Détail des 20 critères pour un sous-projet.
    Le comité voit les résultats automatiques et saisit :
    - décision comité par critère
    - motif comité par critère
    - décision globale comité
    - motif global comité
    """
    utilisateur = get_current_user(request)

    if not can_validate_comite(utilisateur):
        messages.error(request, "❌ Vous n'êtes pas autorisé à accéder au détail de la présélection comité.")
        return redirect('formulaire:liste_sous_projets')

    sous_projet = get_object_or_404(get_accessible_sous_projets(utilisateur), pk=pk)

    # Créer automatiquement les 20 lignes si elles n'existent pas encore
    if not sous_projet.resultats_preselection.exists():
        criteres_auto = evaluer_criteres_preselection(sous_projet)

        for item in criteres_auto:
            decision_auto = item.get('decision', 'À examiner')

            if decision_auto == 'Éligible':
                decision_auto_db = 'eligible'
            elif decision_auto == 'Non éligible':
                decision_auto_db = 'non_eligible'
            else:
                decision_auto_db = 'a_examiner'

            ResultatPreselection.objects.create(
                sous_projet=sous_projet,
                numero_critere=item.get('numero'),
                critere=item.get('critere'),
                question=item.get('question'),
                resultat_automatique=item.get('resultat'),
                decision_automatique=decision_auto_db,
                motif_automatique=item.get('motif'),
            )

    queryset = sous_projet.resultats_preselection.all().order_by('numero_critere')

    if request.method == 'POST':
        formset = ResultatPreselectionFormSet(request.POST, queryset=queryset, prefix='critere')
        decision_form = DecisionComiteSousProjetForm(request.POST, instance=sous_projet, prefix='global')

        if formset.is_valid() and decision_form.is_valid():
            formset.save()

            sous_projet = decision_form.save(commit=False)

            if sous_projet.decision_comite == 'preselectionne':
                sous_projet.status = 'preselectionne'
            elif sous_projet.decision_comite == 'rejete':
                sous_projet.status = 'rejete'
            else:
                sous_projet.status = 'etude'

            sous_projet.save()

            messages.success(request, "✅ Décision du comité enregistrée avec succès.")
            return redirect('formulaire:preselection_comite_liste')

        messages.error(request, "❌ Veuillez corriger les erreurs du formulaire.")

    else:
        formset = ResultatPreselectionFormSet(queryset=queryset, prefix='critere')
        decision_form = DecisionComiteSousProjetForm(instance=sous_projet, prefix='global')

    criteres = list(queryset)

    nb_eligibles = sum(1 for c in criteres if c.decision_automatique == 'eligible')
    nb_non_eligibles = sum(1 for c in criteres if c.decision_automatique == 'non_eligible')
    nb_a_examiner = sum(1 for c in criteres if c.decision_automatique == 'a_examiner')

    context = {
        'sous_projet': sous_projet,
        'formset': formset,
        'decision_form': decision_form,
        'criteres': criteres,
        'nb_eligibles': nb_eligibles,
        'nb_non_eligibles': nb_non_eligibles,
        'nb_a_examiner': nb_a_examiner,
    }

    return render(request, 'formulaire/preselection_comite_detail.html', context)