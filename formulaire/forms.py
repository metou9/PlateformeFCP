from decimal import Decimal

from django import forms
from django.core.validators import RegexValidator
from django.forms import inlineformset_factory, formset_factory, BaseFormSet
from django.forms import BaseInlineFormSet
from django.utils import timezone

from .models import (
    SousProjet, Infrastructure, Equipement, Intrant,
    Fonctionnement, Service, Activite,
    RealisationPassee, PassifEmprunt,
    Wilaya, Moughataa, Commune, Paysage
)


# ============================================
# FORMULAIRE PRINCIPAL SOUS-PROJET
# ============================================

class SousProjetForm(forms.ModelForm):
    """Formulaire principal pour la création d'un sous-projet"""

    date_formulaire = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        error_messages={'required': 'La date du formulaire est obligatoire.'}
    )

    intitule_sous_projet = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=500
    )

    guichet = forms.ChoiceField(
        choices=SousProjet.GUICHET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': 'Le guichet est obligatoire.'}
    )

    type_projet = forms.ChoiceField(
        choices=SousProjet.TYPE_PROJET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_type_projet'}),
        required=True,
        error_messages={'required': 'Le type de projet est obligatoire.'}
    )

    numero_reception_formulaire = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        max_length=100,
        error_messages={'required': 'Le numéro réception formulaire est obligatoire.'}
    )

    nombre_hectare = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2
    )

    chaine_approvisionnement = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=500
    )

    marches_vises = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    segment_ca = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=500
    )

    nom_statut_juridique = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        max_length=500,
        error_messages={'required': 'Le nom et statut juridique est obligatoire.'}
    )

    principal_domaine_activites = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    adresse = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    personne_contact_nom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        max_length=200,
        error_messages={'required': 'Le nom de la personne contact est obligatoire.'}
    )

    personne_contact_fonction = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=200
    )

    telephone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 12345678'}),
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='Le numéro de téléphone doit contenir exactement 8 chiffres.'
            )
        ],
        error_messages={'required': 'Le téléphone est obligatoire.'}
    )

    fax = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 1234'}),
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$',
                message='Le fax doit contenir exactement 4 chiffres.'
            )
        ]
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False,
        error_messages={'invalid': 'Veuillez entrer une adresse email valide.'}
    )

    presente_par_femmes_jeunes = forms.ChoiceField(
        choices=SousProjet.OUI_NON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    objectif_sous_projet = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )

    wilaya = forms.ModelChoiceField(
        queryset=Wilaya.objects.all(),
        empty_label="Sélectionnez une wilaya",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_wilaya'}),
        required=True,
        error_messages={'required': 'La wilaya est obligatoire.'}
    )

    moughataa = forms.ModelChoiceField(
        queryset=Moughataa.objects.none(),
        empty_label="Sélectionnez d'abord une wilaya",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_moughataa'}),
        required=True,
        error_messages={'required': 'La moughataa est obligatoire.'}
    )

    commune = forms.ModelChoiceField(
        queryset=Commune.objects.none(),
        empty_label="Sélectionnez d'abord une moughataa",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_commune'}),
        required=True,
        error_messages={'required': 'La commune est obligatoire.'}
    )

    paysage = forms.ModelChoiceField(
        queryset=Paysage.objects.none(),
        empty_label="Sélectionnez un paysage",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_paysage'}),
        required=True,
        error_messages={'required': 'Le paysage/ZOCA est obligatoire.'}
    )

    village = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'village-list',
            'id': 'id_village',
            'placeholder': 'Saisissez un village'
        }),
        required=True,
        max_length=200,
        error_messages={'required': 'Le village est obligatoire.'}
    )

    annee_debut_activites = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False,
        min_value=1900,
        max_value=2100
    )

    historique_promoteur = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )

    class Meta:
        model = SousProjet
        exclude = ['date_saisie', 'date_creation', 'date_modification']
        widgets = {
            'objectif_sous_projet': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        chosen_wilaya_id = None

        if self.user and getattr(self.user, 'role', None) == 'agent':
            if getattr(self.user, 'wilaya_id', None):
                self.fields['wilaya'].queryset = Wilaya.objects.filter(pk=self.user.wilaya_id)
                self.fields['wilaya'].empty_label = None
                self.fields['wilaya'].initial = self.user.wilaya
                self.fields['wilaya'].help_text = f"Wilaya affectée : {self.user.wilaya.nom}"
                chosen_wilaya_id = self.user.wilaya_id
            else:
                self.fields['wilaya'].queryset = Wilaya.objects.none()

        elif 'wilaya' in self.data:
            try:
                chosen_wilaya_id = int(self.data.get('wilaya'))
            except (ValueError, TypeError):
                chosen_wilaya_id = None

        elif self.instance.pk and self.instance.wilaya_id:
            chosen_wilaya_id = self.instance.wilaya_id

        if chosen_wilaya_id:
            self.fields['moughataa'].queryset = Moughataa.objects.filter(wilaya_id=chosen_wilaya_id).order_by('nom')
        else:
            self.fields['moughataa'].queryset = Moughataa.objects.none()

        chosen_moughataa_id = None
        if 'moughataa' in self.data:
            try:
                chosen_moughataa_id = int(self.data.get('moughataa'))
            except (ValueError, TypeError):
                chosen_moughataa_id = None
        elif self.instance.pk and self.instance.moughataa_id:
            chosen_moughataa_id = self.instance.moughataa_id

        if chosen_moughataa_id:
            self.fields['commune'].queryset = Commune.objects.filter(moughataa_id=chosen_moughataa_id).order_by('nom')
        else:
            self.fields['commune'].queryset = Commune.objects.none()

        chosen_commune_id = None
        if 'commune' in self.data:
            try:
                chosen_commune_id = int(self.data.get('commune'))
            except (ValueError, TypeError):
                chosen_commune_id = None
        elif self.instance.pk and self.instance.commune_id:
            chosen_commune_id = self.instance.commune_id

        if chosen_commune_id:
            self.fields['paysage'].queryset = Paysage.objects.filter(commune_id=chosen_commune_id).order_by('nom')
        else:
            self.fields['paysage'].queryset = Paysage.objects.none()

        for _, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required-field'

    def clean(self):
        cleaned_data = super().clean()
        type_projet = cleaned_data.get('type_projet')
        nombre_hectare = cleaned_data.get('nombre_hectare')

        if type_projet == 'AG' and not nombre_hectare:
            self.add_error('nombre_hectare', "Le nombre hectare est obligatoire pour un projet de type AG.")

        if type_projet != 'AG':
            cleaned_data['nombre_hectare'] = None

        return cleaned_data

    def clean_date_formulaire(self):
        date_formulaire = self.cleaned_data.get('date_formulaire')

        if not date_formulaire:
            return date_formulaire

        if self.instance and self.instance.pk and self.instance.date_saisie:
            date_limite = self.instance.date_saisie.date()
        else:
            date_limite = timezone.localdate()

        if date_formulaire > date_limite:
            raise forms.ValidationError(
                "La date du formulaire doit être antérieure ou égale à la date de saisie."
            )

        return date_formulaire

    def clean_wilaya(self):
        wilaya = self.cleaned_data.get('wilaya')

        if self.user and getattr(self.user, 'role', None) == 'agent':
            if not getattr(self.user, 'wilaya_id', None):
                raise forms.ValidationError("Cet agent n'a pas de wilaya affectée.")
            if not wilaya or wilaya.id != self.user.wilaya_id:
                raise forms.ValidationError("Vous ne pouvez saisir que des sous-projets de votre wilaya.")
            return self.user.wilaya

        return wilaya

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and not telephone.isdigit():
            raise forms.ValidationError('Le numéro de téléphone doit contenir uniquement des chiffres.')
        if telephone and len(telephone) != 8:
            raise forms.ValidationError('Le numéro de téléphone doit contenir exactement 8 chiffres.')
        return telephone

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        if fax and not fax.isdigit():
            raise forms.ValidationError('Le fax doit contenir uniquement des chiffres.')
        if fax and len(fax) != 4:
            raise forms.ValidationError('Le fax doit contenir exactement 4 chiffres.')
        return fax


# ============================================
# FORMULAIRE DES ACTIVITÉS
# ============================================

class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite
        fields = ['nom_activite', 'realisations']
        widgets = {
            'nom_activite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom de l'activité"
            }),
            'realisations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objectifs quantitatifs'
            }),
        }


class BaseActiviteFormSet(BaseInlineFormSet):
    pass


ActiviteFormSet = inlineformset_factory(
    SousProjet,
    Activite,
    form=ActiviteForm,
    extra=0,
    can_delete=True,
    formset=BaseActiviteFormSet
)


# ============================================
# FORMULAIRES DES TABLES DE FINANCEMENT
# ============================================

class BaseOptionalInlineFormSet(BaseInlineFormSet):
    """
    Ignore les lignes totalement vides pour éviter les insertions NULL en base.
    """
    def save_new(self, form, commit=True):
        cleaned_data = getattr(form, 'cleaned_data', None)
        if cleaned_data:
            description = cleaned_data.get('description')
            quantite = cleaned_data.get('quantite')
            prix_unit = cleaned_data.get('prix_unit')

            source_fields = getattr(form, 'source_fields', ())
            has_sources = any(
                cleaned_data.get(field) not in (None, '', 0, 0.0, Decimal('0'), Decimal('0.0'), Decimal('0.00'))
                for field in source_fields
            )

            if description in (None, '') and quantite in (None, '') and prix_unit in (None, '') and not has_sources:
                return None

        return super().save_new(form, commit=commit)


class BaseFinancementForm(forms.ModelForm):
    """
    Base commune pour les validations métier des lignes de financement.
    """
    source_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.required = False

        if 'id' in self.fields:
            self.fields['id'].required = False

        if 'DELETE' in self.fields:
            self.fields['DELETE'].required = False

    def _is_zero_like(self, value):
        return value in (None, '', 0, 0.0, Decimal('0'), Decimal('0.0'), Decimal('0.00'))

    def _has_any_value(self, cleaned_data):
        description = cleaned_data.get('description')
        quantite = cleaned_data.get('quantite')
        prix_unit = cleaned_data.get('prix_unit')

        if description not in (None, ''):
            return True
        if not self._is_zero_like(quantite):
            return True
        if not self._is_zero_like(prix_unit):
            return True

        for field in self.source_fields:
            value = cleaned_data.get(field)
            if not self._is_zero_like(value):
                return True

        return False

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('DELETE'):
            return cleaned_data

        description = cleaned_data.get('description')
        quantite = cleaned_data.get('quantite')
        prix_unit = cleaned_data.get('prix_unit')

        if not self._has_any_value(cleaned_data):
            cleaned_data['description'] = ''
            cleaned_data['quantite'] = None
            cleaned_data['prix_unit'] = None
            for field in self.source_fields:
                cleaned_data[field] = None
            return cleaned_data

        if not description:
            self.add_error('description', "La description est obligatoire si une ligne de financement est renseignée.")

        if description:
            if quantite in (None, ''):
                self.add_error('quantite', "La quantité est obligatoire si la description est renseignée.")
            if prix_unit in (None, ''):
                self.add_error('prix_unit', "Le prix unitaire est obligatoire si la description est renseignée.")

        for field in self.source_fields:
            if cleaned_data.get(field) in (None, ''):
                cleaned_data[field] = Decimal('0')

        if self.errors:
            return cleaned_data

        montant_total = Decimal(quantite) * Decimal(prix_unit)
        total_sources = sum(Decimal(cleaned_data.get(field) or 0) for field in self.source_fields)

        if total_sources != montant_total:
            raise forms.ValidationError(
                f"Incohérence de financement : le montant total calculé ({montant_total}) doit être égal à la somme des sources ({total_sources})."
            )

        return cleaned_data


class InfrastructureForm(BaseFinancementForm):
    source_fields = ('subvention_padisam', 'contribution_promoteur', 'autre_financement')

    class Meta:
        model = Infrastructure
        fields = [
            'description', 'quantite', 'prix_unit',
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
            'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
            'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
            'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
            'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
        }


class EquipementForm(BaseFinancementForm):
    source_fields = ('subvention_padisam', 'contribution_promoteur', 'autre_financement')

    class Meta:
        model = Equipement
        fields = [
            'description', 'quantite', 'prix_unit',
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
            'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
            'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
            'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
            'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
        }


class IntrantForm(BaseFinancementForm):
    source_fields = ('subvention_padisam', 'contribution_promoteur', 'autre_financement')

    class Meta:
        model = Intrant
        fields = [
            'description', 'quantite', 'prix_unit',
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
            'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
            'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
            'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
            'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
        }


class FonctionnementForm(BaseFinancementForm):
    source_fields = ('contribution_promoteur', 'autre_financement')

    class Meta:
        model = Fonctionnement
        fields = [
            'description', 'quantite', 'prix_unit',
            'contribution_promoteur', 'autre_financement'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
            'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
            'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
            'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
        }


class ServiceForm(BaseFinancementForm):
    source_fields = ('subvention_padisam', 'contribution_promoteur', 'autre_financement')

    class Meta:
        model = Service
        fields = [
            'description', 'quantite', 'prix_unit',
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
            'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
            'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
            'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
            'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
        }


# ============================================
# FORMSETS DES TABLES DE FINANCEMENT
# ============================================

InfrastructureFormSet = inlineformset_factory(
    SousProjet, Infrastructure,
    form=InfrastructureForm,
    extra=3,
    can_delete=True,
    formset=BaseOptionalInlineFormSet
)

EquipementFormSet = inlineformset_factory(
    SousProjet, Equipement,
    form=EquipementForm,
    extra=3,
    can_delete=True,
    formset=BaseOptionalInlineFormSet
)

IntrantFormSet = inlineformset_factory(
    SousProjet, Intrant,
    form=IntrantForm,
    extra=3,
    can_delete=True,
    formset=BaseOptionalInlineFormSet
)

FonctionnementFormSet = inlineformset_factory(
    SousProjet, Fonctionnement,
    form=FonctionnementForm,
    extra=1,
    can_delete=True,
    formset=BaseOptionalInlineFormSet
)

ServiceFormSet = inlineformset_factory(
    SousProjet, Service,
    form=ServiceForm,
    extra=1,
    can_delete=True,
    formset=BaseOptionalInlineFormSet
)


# ============================================
# FORMULAIRE DES RÉALISATIONS PASSÉES
# ============================================

class RealisationPasseeForm(forms.ModelForm):
    class Meta:
        model = RealisationPassee
        fields = [
            'produit',
            'volume_annee_1', 'ventes_usd_annee_1', 'prix_vente_mru_annee_1',
            'volume_annee_2', 'ventes_usd_annee_2', 'prix_vente_mru_annee_2',
            'volume_annee_3', 'ventes_usd_annee_3', 'prix_vente_mru_annee_3',
        ]
        widgets = {
            'produit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Produit'
            }),
            'volume_annee_1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ventes_usd_annee_1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente_mru_annee_1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            'volume_annee_2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ventes_usd_annee_2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente_mru_annee_2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            'volume_annee_3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ventes_usd_annee_3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente_mru_annee_3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()

        produit = cleaned_data.get('produit')

        volume_1 = cleaned_data.get('volume_annee_1')
        ventes_1 = cleaned_data.get('ventes_usd_annee_1')
        prix_1 = cleaned_data.get('prix_vente_mru_annee_1')

        volume_2 = cleaned_data.get('volume_annee_2')
        ventes_2 = cleaned_data.get('ventes_usd_annee_2')
        prix_2 = cleaned_data.get('prix_vente_mru_annee_2')

        volume_3 = cleaned_data.get('volume_annee_3')
        ventes_3 = cleaned_data.get('ventes_usd_annee_3')
        prix_3 = cleaned_data.get('prix_vente_mru_annee_3')

        has_data = any([
            produit,
            volume_1, ventes_1, prix_1,
            volume_2, ventes_2, prix_2,
            volume_3, ventes_3, prix_3,
        ])

        # ligne totalement vide = autorisée
        if not has_data:
            return cleaned_data

        # si l'utilisateur commence une ligne, on exige seulement le produit
        if not produit:
            self.add_error('produit', "Le produit est obligatoire si vous saisissez une réalisation.")

        return cleaned_data


class BaseRealisationFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        # Les réalisations passées ne sont pas obligatoires.
        return


# ============================================
# FORMULAIRE DES EMPRUNTS
# ============================================

class PassifEmpruntForm(forms.ModelForm):
    class Meta:
        model = PassifEmprunt
        fields = ['annee', 'institution_financiere', 'montant_emprunte', 'montant_rembourse']
        widgets = {
            'annee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Année'
            }),
            'institution_financiere': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Institution financière'
            }),
            'montant_emprunte': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Montant emprunté'
            }),
            'montant_rembourse': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Montant remboursé'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()

        annee = cleaned_data.get('annee')
        institution = cleaned_data.get('institution_financiere')
        montant_emprunte = cleaned_data.get('montant_emprunte')
        montant_rembourse = cleaned_data.get('montant_rembourse')

        has_data = (
            annee not in (None, '')
            or institution not in (None, '')
            or montant_emprunte not in (None, '')
            or montant_rembourse not in (None, '')
        )

        # ligne totalement vide = autorisée
        if not has_data:
            return cleaned_data

        # si une ligne est commencée, on exige les champs principaux
        if not annee:
            self.add_error('annee', "L'année est obligatoire si vous saisissez un emprunt.")
        if not institution:
            self.add_error('institution_financiere', "L'institution financière est obligatoire si vous saisissez un emprunt.")
        if montant_emprunte in (None, ''):
            self.add_error('montant_emprunte', "Le montant emprunté est obligatoire si vous saisissez un emprunt.")
        if montant_rembourse in (None, ''):
            self.add_error('montant_rembourse', "Le montant remboursé est obligatoire si vous saisissez un emprunt.")

        if self.errors:
            return cleaned_data

        if montant_rembourse > montant_emprunte:
            self.add_error(
                'montant_rembourse',
                "Le montant remboursé doit être inférieur ou égal au montant emprunté."
            )

        return cleaned_data


class BaseEmpruntFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        # Les emprunts ne sont pas obligatoires.
        return


# ============================================
# FORMSETS FINAUX : RÉALISATIONS / EMPRUNTS
# ============================================

RealisationFormSet = formset_factory(
    RealisationPasseeForm,
    formset=BaseRealisationFormSet,
    extra=7,
    max_num=20,
    validate_max=False,
    can_delete=False,
    can_order=False
)

EmpruntFormSet = formset_factory(
    PassifEmpruntForm,
    formset=BaseEmpruntFormSet,
    extra=3,
    max_num=10,
    validate_max=False,
    can_delete=False,
    can_order=False
)