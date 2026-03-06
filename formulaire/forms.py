from django import forms
from django.forms import formset_factory, BaseFormSet
from django.forms import inlineformset_factory
from .models import (
    SousProjet, Infrastructure, Equipement, Intrant,
    RealisationPassee, PassifEmprunt,
    Wilaya, Moughataa, Commune, Village
)

class SousProjetForm(forms.ModelForm):
    date_formulaire = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    class Meta:
        model = SousProjet
        exclude = ['date_saisie', 'date_creation', 'date_modification']
        widgets = {
            'intitule_sous_projet': forms.TextInput(attrs={'class': 'form-control'}),
            'type_sous_projet_demande': forms.TextInput(attrs={'class': 'form-control'}),
            'guichet': forms.Select(attrs={'class': 'form-control'}),
            'type_projet': forms.Select(attrs={'class': 'form-control'}),
            'chaine_approvisionnement': forms.TextInput(attrs={'class': 'form-control'}),
            'marches_vises': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'segment_ca': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_statut_juridique': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'principal_domaine_activites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'personne_contact_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'personne_contact_fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'presente_par_femmes_jeunes': forms.Select(attrs={'class': 'form-control'}),
            'objectif_sous_projet': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'principales_activites': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'village': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du village/quartier'}),
            'annee_debut_activites': forms.NumberInput(attrs={'class': 'form-control'}),
            'historique_promoteur': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            
            # Nouveaux champs pour fonctionnement
            'fonctionnement_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description du fonctionnement'}),
            'fonctionnement_quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'fonctionnement_montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'fonctionnement_contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control'}),
            'fonctionnement_autre_financement': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Nouveaux champs pour services
            'service_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description du service'}),
            'service_quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_subvention_padisam': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_autre_financement': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre tous les champs de localisation NON obligatoires pour le test
        self.fields['wilaya'].required = False
        self.fields['moughataa'].required = False
        self.fields['commune'].required = False
        
        # Afficher TOUTES les moughataas et communes sans filtre
        self.fields['moughataa'].queryset = Moughataa.objects.all()
        self.fields['commune'].queryset = Commune.objects.all()
# Création des formulaires pour les tables enfants (formsets)
InfrastructureFormSet = inlineformset_factory(
    SousProjet, Infrastructure,
    fields=['description', 'quantite', 'montant_total', 'subvention_padisam', 
            'contribution_promoteur', 'autre_financement'],
    extra=3,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        'montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

EquipementFormSet = inlineformset_factory(
    SousProjet, Equipement,
    fields=['description', 'quantite', 'montant_total', 'subvention_padisam',
            'contribution_promoteur', 'autre_financement'],
    extra=3,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        'montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

IntrantFormSet = inlineformset_factory(
    SousProjet, Intrant,
    fields=['description', 'quantite', 'montant_total', 'subvention_padisam',
            'contribution_promoteur', 'autre_financement'],
    extra=3,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control'}),
        'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        'montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
        'subvention_padisam': forms.NumberInput(attrs={'class': 'form-control'}),
        'contribution_promoteur': forms.NumberInput(attrs={'class': 'form-control'}),
        'autre_financement': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)



# Formulaire pour une réalisation passée (une ligne)
class RealisationPasseeForm(forms.ModelForm):
    class Meta:
        model = RealisationPassee
        fields = ['annee', 'produit', 'volume', 'ventes_usd']
        widgets = {
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année'}),
            'produit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Produit'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Volume'}),
            'ventes_usd': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ventes USD'}),
        }

# Formulaire pour un emprunt (une ligne)
class PassifEmpruntForm(forms.ModelForm):
    class Meta:
        model = PassifEmprunt
        fields = ['annee', 'institution_financiere', 'montant_emprunte', 'montant_rembourse']
        widgets = {
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année'}),
            'institution_financiere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institution'}),
            'montant_emprunte': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant emprunté'}),
            'montant_rembourse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant remboursé'}),
        }

# Formset pour 3 réalisations fixes
class BaseRealisationFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force 3 formulaires
        self.extra = 3
        self.max_num = 3
        self.min_num = 3
        self.validate_min = True
        self.validate_max = True
    
    def clean(self):
        """Vérifie qu'il y a exactement 3 formulaires"""
        if any(self.errors):
            return
        if len(self.forms) != 3:
            raise forms.ValidationError("Vous devez fournir exactement 3 années de réalisations")

# Formset pour 3 emprunts fixes
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
            raise forms.ValidationError("Vous devez fournir exactement 3 années d'emprunts")

# Créer les formsets avec exactement 3 formulaires
RealisationFormSet = formset_factory(
    RealisationPasseeForm,
    formset=BaseRealisationFormSet,
    extra=3,
    max_num=3,
    min_num=3,
    validate_min=True,
    validate_max=True,
    can_delete=False,  # Pas de suppression
    can_order=False    # Pas de réorganisation
)

EmpruntFormSet = formset_factory(
    PassifEmpruntForm,
    formset=BaseEmpruntFormSet,
    extra=3,
    max_num=3,
    min_num=3,
    validate_min=True,
    validate_max=True,
    can_delete=False,  # Pas de suppression
    can_order=False    # Pas de réorganisation
)