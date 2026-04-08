from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.forms import inlineformset_factory, formset_factory, BaseFormSet
from django.forms import BaseInlineFormSet

from .models import (
    SousProjet, Infrastructure, Equipement, Intrant,
    Fonctionnement, Service, Activite,
    RealisationPassee, PassifEmprunt,
    Wilaya, Moughataa, Commune, Paysage, Village
)

# ============================================
# FORMULAIRE PRINCIPAL SOUS-PROJET
# ============================================

class SousProjetForm(forms.ModelForm):
    """Formulaire principal pour la création d'un sous-projet"""
    
    # ============================================
    # CHAMPS AVEC VALIDATIONS SPÉCIFIQUES
    # ============================================
    
    # Date du formulaire - OBLIGATOIRE
    date_formulaire = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        error_messages={'required': 'La date du formulaire est obligatoire.'}
    )
    
    # Intitulé du sous-projet - OBLIGATOIRE
    intitule_sous_projet = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        max_length=500,
        error_messages={'required': "L'intitulé du sous-projet est obligatoire."}
    )
    
    # Guichet - OBLIGATOIRE
    guichet = forms.ChoiceField(
        choices=SousProjet.GUICHET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': 'Le guichet est obligatoire.'}
    )
    
    # Type projet - OBLIGATOIRE
    type_projet = forms.ChoiceField(
        choices=SousProjet.TYPE_PROJET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': 'Le type de projet est obligatoire.'}
    )
    
    # Chaîne d'approvisionnement - NON OBLIGATOIRE
    chaine_approvisionnement = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=500
    )
    
    # Marchés visés - OBLIGATOIRE
    marches_vises = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True,
        error_messages={'required': 'Les marchés visés sont obligatoires.'}
    )
    
    # Segment de la CA - NON OBLIGATOIRE
    segment_ca = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=500
    )
    
    # Nom et statut juridique - NON OBLIGATOIRE
    nom_statut_juridique = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=500
    )
    
    # Principal domaine d'activités - NON OBLIGATOIRE
    principal_domaine_activites = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    
    # Adresse - NON OBLIGATOIRE
    adresse = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    
    # Personne contact (nom) - NON OBLIGATOIRE
    personne_contact_nom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=200
    )
    
    # Personne contact (fonction) - NON OBLIGATOIRE
    personne_contact_fonction = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=200
    )
    
    # Téléphone - NON OBLIGATOIRE mais validation si rempli (8 chiffres)
    telephone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 12345678'}),
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='Le numéro de téléphone doit contenir exactement 8 chiffres.'
            )
        ]
    )
    
    # Fax - NON OBLIGATOIRE mais validation si rempli (4 chiffres)
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
    
    # Email - NON OBLIGATOIRE
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False,
        error_messages={'invalid': 'Veuillez entrer une adresse email valide.'}
    )
    
    # Femmes/jeunes? - NON OBLIGATOIRE
    presente_par_femmes_jeunes = forms.ChoiceField(
        choices=SousProjet.OUI_NON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    # Wilaya - OBLIGATOIRE
    wilaya = forms.ModelChoiceField(
        queryset=Wilaya.objects.all(),
        empty_label="Sélectionnez une wilaya",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_wilaya'}),
        required=True,
        error_messages={'required': 'La wilaya est obligatoire.'}
    )
    
    # Moughataa - OBLIGATOIRE
    moughataa = forms.ModelChoiceField(
        queryset=Moughataa.objects.none(),
        empty_label="Sélectionnez d'abord une wilaya",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_moughataa'}),
        required=True,
        error_messages={'required': 'La moughataa est obligatoire.'}
    )
    
    # Commune - OBLIGATOIRE
    commune = forms.ModelChoiceField(
        queryset=Commune.objects.none(),
        empty_label="Sélectionnez d'abord une moughataa",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_commune'}),
        required=True,
        error_messages={'required': 'La commune est obligatoire.'}
    )
    
    # Paysage/ZOCA - OBLIGATOIRE
    paysage = forms.ModelChoiceField(
        queryset=Paysage.objects.none(),
        empty_label="Sélectionnez un paysage",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_paysage'}),
        required=True,
        error_messages={'required': 'Le paysage/ZOCA est obligatoire.'}
    )
    
    # Village - OBLIGATOIRE
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
    
    # Année début activités - NON OBLIGATOIRE
    annee_debut_activites = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False,
        min_value=1900,
        max_value=2100
    )
    
    # Historique - NON OBLIGATOIRE
    historique_promoteur = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )
    
    class Meta:
        model = SousProjet
        exclude = ['date_saisie', 'date_creation', 'date_modification']
        
        # Les widgets sont déjà définis dans les champs ci-dessus
        # On garde uniquement les champs qui n'ont pas été redéfinis
        widgets = {
            'objectif_sous_projet': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'principales_activites': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialiser les querysets pour les champs dynamiques
        self.fields['moughataa'].queryset = Moughataa.objects.all()
        self.fields['commune'].queryset = Commune.objects.all()
        self.fields['paysage'].queryset = Paysage.objects.none()
        
        # Chargement dynamique des paysages
        if 'commune' in self.data:
            try:
                commune_id = int(self.data.get('commune'))
                self.fields['paysage'].queryset = Paysage.objects.filter(commune_id=commune_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.commune:
            self.fields['paysage'].queryset = Paysage.objects.filter(commune=self.instance.commune)
        
        # Ajouter les classes CSS pour les champs obligatoires (optionnel)
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required-field'

class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite
        fields = ['nom_activite', 'realisations']
        widgets = {
            'nom_activite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'activité'}),
            'realisations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Objectifs quantitatifs, réalisations...'}),
        }


class BaseActiviteFormSet(BaseInlineFormSet):
    """Formset pour les activités avec possibilité d'ajout/suppression"""
    pass


# Formset pour les activités (plusieurs lignes possibles)
ActiviteFormSet = inlineformset_factory(
    SousProjet, Activite,
    form=ActiviteForm,
    extra=3,           # 3 lignes vides par défaut
    can_delete=True,   # L'utilisateur peut supprimer une ligne
    formset=BaseActiviteFormSet
)           
    
    # ============================================
    # VALIDATION SUPPLÉMENTAIRE POUR LE TÉLÉPHONE ET FAX
    # ============================================
    
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
# FORMSETS POUR LES TABLES DE FINANCEMENT
# ============================================

# A. INFRASTRUCTURES
InfrastructureFormSet = inlineformset_factory(
    SousProjet, Infrastructure,
    fields=['description', 'quantite', 'prix_unit',  
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'],
    extra=3,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
        'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
    }
)

# B. EQUIPEMENTS
EquipementFormSet = inlineformset_factory(
    SousProjet, Equipement,
    fields=['description', 'quantite', 'prix_unit',
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'],
    extra=3,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
        'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
    }
)

# C. INTRANTS
IntrantFormSet = inlineformset_factory(
    SousProjet, Intrant,
    fields=['description', 'quantite', 'prix_unit', 
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'],
    extra=3,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
        'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
    }
)

# D. FONCTIONNEMENT
FonctionnementFormSet = inlineformset_factory(
    SousProjet, Fonctionnement,
    fields=['description', 'quantite', 'prix_unit', 
            'contribution_promoteur', 'autre_financement'],
    extra=1,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
        'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
    }
)

# E. SERVICES
ServiceFormSet = inlineformset_factory(
    SousProjet, Service,
    fields=['description', 'quantite', 'prix_unit',  
            'subvention_padisam', 'contribution_promoteur', 'autre_financement'],
    extra=1,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
        'prix_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'step': '1'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subvention PADISAM', 'step': '1'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution promoteur', 'step': '1'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Autre financement', 'step': '1'}),
    }
)


# ============================================
# FORMULAIRES POUR LES RÉALISATIONS (3 lignes fixes)
# ============================================

class RealisationPasseeForm(forms.ModelForm):
    class Meta:
        model = RealisationPassee
        fields = ['annee', 'produit', 'volume', 'ventes_usd']
        widgets = {
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année'}),
            'produit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Produit'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Volume', 'step': '1'}),
            'ventes_usd': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ventes USD', 'step': '1'}),
        }


class BaseRealisationFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = 3
        self.max_num = 3
        self.min_num = 3
        self.validate_min = True
        self.validate_max = True
    
    def clean(self):
        if any(self.errors):
            return
        if len(self.forms) != 3:
            raise forms.ValidationError("❌ Vous devez fournir exactement 3 années de réalisations.")
        return self.forms





# ============================================
# FORMULAIRES POUR LES EMPRUNTS (3 lignes fixes)
# ============================================

class PassifEmpruntForm(forms.ModelForm):
    class Meta:
        model = PassifEmprunt
        fields = ['annee', 'institution_financiere', 'montant_emprunte', 'montant_rembourse']
        widgets = {
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année'}),
            'institution_financiere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institution'}),
            'montant_emprunte': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant emprunté', 'step': '1'}),
            'montant_rembourse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant remboursé', 'step': '1'}),
        }


class BaseEmpruntFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = 3
        self.max_num = 3
        self.min_num = 3
        self.validate_min = True
        self.validate_max = True
    
    def clean(self):
        if any(self.errors):
            return
        if len(self.forms) != 3:
            raise forms.ValidationError("❌ Vous devez fournir exactement 3 années d'emprunts.")
        return self.forms


# ============================================
# CRÉATION DES FORMSETS FINAUX
# ============================================

RealisationFormSet = formset_factory(
    RealisationPasseeForm,
    formset=BaseRealisationFormSet,
    extra=3,
    max_num=3,
    min_num=3,
    validate_min=True,
    validate_max=True,
    can_delete=False,
    can_order=False
)

EmpruntFormSet = formset_factory(
    PassifEmpruntForm,
    formset=BaseEmpruntFormSet,
    extra=3,
    max_num=3,
    min_num=3,
    validate_min=True,
    validate_max=True,
    can_delete=False,
    can_order=False
)