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
)
from .models import (
    SousProjet,
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


def get_accessible_sous_projets(utilisateur):
    """
    Sous-projets visibles selon le rôle.
    - Agent : seulement sa wilaya
    - Autres rôles : tous
    """
    queryset = SousProjet.objects.all()

    if is_agent_saisie(utilisateur):
        if utilisateur.wilaya_id:
            queryset = queryset.filter(wilaya_id=utilisateur.wilaya_id)
        else:
            queryset = queryset.none()

    return queryset


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

    context = {
        'user_name': request.session.get('user_name'),
        'user_role': request.session.get('user_role'),
        'user_wilaya_nom': request.session.get('user_wilaya_nom'),
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


def preselection_automatique(request):
    """
    Page simple de démonstration de la présélection automatique.
    """
    sous_projets = SousProjet.objects.all().order_by("-id")

    lignes = [evaluer_preselection(sp) for sp in sous_projets]

    context = {
        "lignes": lignes,
        "total_dossiers": sous_projets.count(),
    }
    return render(request, "formulaire/preselection_automatique.html", context)