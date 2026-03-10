from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password


# ============================================
# 1. MODÈLES DE RÉFÉRENCE (Tables déjà existantes)
# ============================================

class Wilaya(models.Model):
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.code} - {self.nom}"

class Moughataa(models.Model):
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name='moughataas')
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nom} ({self.wilaya.nom})"

class Commune(models.Model):
    moughataa = models.ForeignKey(Moughataa, on_delete=models.CASCADE, related_name='communes')
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nom}"

class Village(models.Model):
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='villages')
    nom = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nom} ({self.commune.nom})"


# ============================================
# 2. TABLE PRINCIPALE : SOUS-PROJET
# ============================================

class SousProjet(models.Model):
    # Choix pour les champs avec valeurs prédéfinies
    GUICHET_CHOICES = [
        ('AGR', 'AGR'),
        ('ACI', 'ACI'),
    ]
    
    TYPE_PROJET_CHOICES = [
        ('AG', 'AG'),
        ('EL', 'EL'),
        ('ENV', 'ENV'),
    ]
    
    OUI_NON_CHOICES = [
        ('oui', 'Oui'),
        ('non', 'Non'),
    ]
    
    # 1. Informations générales
    date_saisie = models.DateTimeField(auto_now_add=True)  # Date système automatique
    date_formulaire = models.DateField()  # Date saisie manuellement
    intitule_sous_projet = models.CharField(max_length=500)
    
    type_sous_projet_demande = models.CharField(max_length=200)
    guichet = models.CharField(max_length=3, choices=GUICHET_CHOICES)
    type_projet = models.CharField(max_length=3, choices=TYPE_PROJET_CHOICES)
    chaine_approvisionnement = models.CharField(max_length=500)
    marches_vises = models.TextField(help_text="Marchés visés / clients identifiés")
    segment_ca = models.CharField(max_length=500)
    
    # 2. Identification du demandeur
    nom_statut_juridique = models.CharField(max_length=500)
    adresse = models.TextField()
    principal_domaine_activites = models.TextField()
    personne_contact_nom = models.CharField(max_length=200)
    personne_contact_fonction = models.CharField(max_length=200)
    telephone = models.CharField(max_length=50)
    fax = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    
    # Question femmes/jeunes
    presente_par_femmes_jeunes = models.CharField(
        max_length=3, 
        choices=OUI_NON_CHOICES,
        verbose_name="Présenté par des femmes ou jeunes (-35 ans)"
    )
    
    # 3. Description
    objectif_sous_projet = models.TextField()
    principales_activites = models.TextField(
        help_text="Liste des principales activités avec objectifs quantitatifs"
    )
    
    # Localisation
    wilaya = models.ForeignKey(Wilaya, on_delete=models.PROTECT)
    moughataa = models.ForeignKey(Moughataa, on_delete=models.PROTECT)
    commune = models.ForeignKey(Commune, on_delete=models.PROTECT)
    village = models.CharField(max_length=200, blank=True, null=True, 
    help_text="Nom du village ou quartier")    
    # 5. Renseignement sur le promoteur
    annee_debut_activites = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    historique_promoteur = models.TextField(verbose_name="Brève historique")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.intitule_sous_projet} - {self.date_formulaire}"
     # === FONCTIONNEMENT (une seule ligne) ===
    fonctionnement_description = models.CharField(max_length=500, blank=True, null=True)
    fonctionnement_quantite = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    fonctionnement_montant_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    fonctionnement_contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    fonctionnement_autre_financement = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)

    # === SERVICES (une seule ligne) ===
    service_description = models.CharField(max_length=500, blank=True, null=True)
    service_quantite = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    service_montant_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    service_subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    service_contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    service_autre_financement = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)


# ============================================
# 3. TABLES DE FINANCEMENT (Infrastructure)
# ============================================

class Infrastructure(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='infrastructures')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    montant_total = models.DecimalField(max_digits=15, decimal_places=2)
    subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Infra - {self.sous_projet.id} - {self.description[:30]}"


class Equipement(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='equipements')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    montant_total = models.DecimalField(max_digits=15, decimal_places=2)
    subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Équip - {self.sous_projet.id} - {self.description[:30]}"


class Intrant(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='intrants')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    montant_total = models.DecimalField(max_digits=15, decimal_places=2)
    subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Intrant - {self.sous_projet.id} - {self.description[:30]}"




# ============================================
# 4. TABLE DES RÉALISATIONS PASSÉES
# ============================================

class RealisationPassee(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='realisations')
    annee = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    produit = models.CharField(max_length=500)
    volume = models.DecimalField(max_digits=15, decimal_places=2, help_text="Volume en tonnes/kg selon produit")
    ventes_usd = models.DecimalField(max_digits=15, decimal_places=2, help_text="Ventes en USD")
    
    class Meta:
        ordering = ['annee']
        # Optionnel : ajouter une contrainte pour 3 maximum (mais on gérera dans le formulaire)
    
    def __str__(self):
        return f"Réalisation {self.annee} - {self.produit[:30]}"


# ============================================
# 5. TABLE DES PASSIFS (EMPRUNTS)
# ============================================

class PassifEmprunt(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='emprunts')
    annee = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    institution_financiere = models.CharField(max_length=200)
    montant_emprunte = models.DecimalField(max_digits=15, decimal_places=2)
    montant_rembourse = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        ordering = ['annee']
    
    def __str__(self):
        return f"Emprunt {self.annee} - {self.institution_financiere[:20]}"

# ============================================
# 5. TABLE UTILISATEUR
# ============================================
class Utilisateur(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('agent', 'Agent de saisie'),
        ('superviseur', 'Superviseur'),
        ('consultant', 'Consultant'),
    ]
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # Le mot de passe sera hashé
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    email = models.EmailField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    dernier_login = models.DateTimeField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    def set_password(self, raw_password):
        """Hash le mot de passe"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Vérifie le mot de passe"""
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.username})"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"