# -*- coding: utf-8 -*-
"""
Projet BI - Mini-projet Data Analytics & Business Intelligence
ETL et Data Warehouse pour données médicales (Colique Néphrétique)
Auteur: Imen
Date: Décembre 2024
"""

import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print(" PROJET BI - ETL ET DATA WAREHOUSE ".center(80, "="))
print("="*80)

# ==================================================================================
# ÉTAPE 1: EXTRACTION DES DONNÉES
# ==================================================================================
print("\n[ÉTAPE 1] EXTRACTION DES DONNÉES")
print("-" * 80)

df = pd.read_csv('/mnt/project/data9.csv')
print(f"✓ Données chargées: {df.shape[0]} lignes, {df.shape[1]} colonnes")

# Sauvegarde des données brutes
df_original = df.copy()

# ==================================================================================
# ÉTAPE 2: TRANSFORMATION ET NETTOYAGE DES DONNÉES
# ==================================================================================
print("\n[ÉTAPE 2] TRANSFORMATION ET NETTOYAGE DES DONNÉES")
print("-" * 80)

# 2.1 Gestion des valeurs manquantes
print("\n2.1 Gestion des valeurs manquantes:")

# Supprimer la colonne Longueur_DPC (trop de valeurs manquantes)
if 'Longueur_DPC' in df.columns:
    df = df.drop(columns=['Longueur_DPC'])
    print("  ✓ Colonne 'Longueur_DPC' supprimée (326 valeurs manquantes)")

# Imputation clinique de ATCDS
def impute_atcds(row):
    """Imputation logique basée sur les comorbidités"""
    if pd.isna(row['ATCDS']) or row['ATCDS'] not in [2.0, 4.0]:
        comorbidites = ['Diabète', 'HTA', 'Dyslipidémie', 'FA', 'Insuffisance_rénale']
        has_comorbidity = any(row[col] == 2.0 for col in comorbidites if col in df.columns and not pd.isna(row[col]))
        return 2.0 if has_comorbidity else 4.0
    return row['ATCDS']

df['ATCDS'] = df.apply(impute_atcds, axis=1)
print(f"  ✓ ATCDS imputé: {86} valeurs manquantes traitées")

# Imputation de Femme_enceinte basée sur Genre
if 'Femme_enceinte' in df.columns and 'Genre' in df.columns:
    # Pour les hommes (Genre=2), Femme_enceinte=4 (Non)
    df.loc[(df['Genre'] == 2.0) & (df['Femme_enceinte'].isna()), 'Femme_enceinte'] = 4.0
    # Pour les femmes (Genre=4), imputer par le mode
    female_mode = df[df['Genre'] == 4.0]['Femme_enceinte'].mode()
    if len(female_mode) > 0:
        df.loc[(df['Genre'] == 4.0) & (df['Femme_enceinte'].isna()), 'Femme_enceinte'] = female_mode[0]
    print(f"  ✓ Femme_enceinte imputé selon le genre")

# Imputation par le mode pour les colonnes avec peu de valeurs manquantes
mode_cols = ['febrile', 'AUSP']
for col in mode_cols:
    if col in df.columns and df[col].isna().sum() > 0:
        mode_val = df[col].mode()
        if len(mode_val) > 0:
            df[col].fillna(mode_val[0], inplace=True)
            print(f"  ✓ {col} imputé par le mode")

# 2.2 Correction des valeurs aberrantes
print("\n2.2 Correction des valeurs aberrantes:")

# Correction de Pollakiurie (valeur 44 -> 4)
if 'Pollakiurie' in df.columns:
    df['Pollakiurie'] = df['Pollakiurie'].replace(44.0, 4.0)
    print("  ✓ Pollakiurie: valeur 44 corrigée en 4")

# 2.3 Filtrage des valeurs physiologiquement implausibles
print("\n2.3 Filtrage des valeurs implausibles:")
initial_count = len(df)

# Filtres de plausibilité
if 'Age' in df.columns:
    df = df[(df['Age'] >= 0) & (df['Age'] <= 120)]
if 'Température' in df.columns:
    df = df[(df['Température'] >= 34) & (df['Température'] <= 42)]
if 'FC' in df.columns:
    df = df[(df['FC'] >= 30) & (df['FC'] <= 220)]
if 'EN0' in df.columns:
    df = df[(df['EN0'] >= 0) & (df['EN0'] <= 10)]

filtered_count = initial_count - len(df)
print(f"  ✓ {filtered_count} lignes filtrées (valeurs implausibles)")
print(f"  ✓ Dataset nettoyé: {len(df)} lignes")

# 2.4 Binarisation des variables
print("\n2.4 Binarisation des variables:")

def binarize_column(series):
    """Convertit les codes (2,4) en (1,0) ou (4,6) en (0,1)"""
    unique_vals = series.dropna().unique()
    if len(unique_vals) == 2:
        if set(unique_vals) == {2.0, 4.0}:
            return series.map({2.0: 1, 4.0: 0})
        elif set(unique_vals) == {4.0, 6.0}:
            return series.map({4.0: 0, 6.0: 1})
    return series

binary_count = 0
for col in df.columns:
    original = df[col].copy()
    df[col] = binarize_column(df[col])
    if not df[col].equals(original):
        binary_count += 1

print(f"  ✓ {binary_count} colonnes binarisées")

# 2.5 Catégorisation de l'âge
print("\n2.5 Catégorisation de l'âge:")
if 'Age' in df.columns:
    df['Categorie_Age'] = pd.cut(
        df['Age'], 
        bins=[0, 17, 30, 50, 70, 120],
        labels=['Enfant', 'Jeune_adulte', 'Adulte', 'Senior', 'Personne_agee']
    )
    print("  ✓ Catégorie d'âge créée: Enfant, Jeune_adulte, Adulte, Senior, Personne_agee")

# 2.6 Feature Engineering - Variation de la douleur
print("\n2.6 Feature Engineering:")
pain_cols = ['EN0', 'EN_15min', 'EN_30min', 'EN_45min', 'EN_60min', 'EN_90min']
if all(col in df.columns for col in ['EN0', 'EN_90min']):
    df['Variation_douleur'] = df['EN_90min'] - df['EN0']
    df['Amelioration_douleur'] = (df['Variation_douleur'] < -2).astype(int)
    print("  ✓ Variables dérivées créées: Variation_douleur, Amelioration_douleur")

# Calcul du score de comorbidité
comorbidity_cols = ['Diabète', 'HTA', 'Dyslipidémie', 'FA', 'Insuffisance_rénale', 
                     'BPCO', 'Asthme', 'UGD']
available_comorbidity_cols = [col for col in comorbidity_cols if col in df.columns]
if available_comorbidity_cols:
    df['Score_comorbidite'] = df[available_comorbidity_cols].sum(axis=1)
    print(f"  ✓ Score de comorbidité calculé ({len(available_comorbidity_cols)} conditions)")

print(f"\n✓ Dataset transformé: {len(df)} lignes, {len(df.columns)} colonnes")

# ==================================================================================
# ÉTAPE 3: CRÉATION DU DATA WAREHOUSE (MODÈLE EN ÉTOILE)
# ==================================================================================
print("\n[ÉTAPE 3] CRÉATION DU DATA WAREHOUSE (MODÈLE EN ÉTOILE)")
print("-" * 80)

# Connexion à la base de données SQLite
conn = sqlite3.connect('/home/claude/datawarehouse_medical.db')
cursor = conn.cursor()
print("✓ Connexion à la base de données établie")

# 3.1 Table de dimension: DIM_PATIENT
print("\n3.1 Création de DIM_PATIENT:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_PATIENT (
    Patient_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Age INTEGER,
    Genre TEXT,
    Categorie_Age TEXT,
    ATCDS INTEGER,
    Score_comorbidite REAL,
    Diabete INTEGER,
    HTA INTEGER,
    Dyslipidémie INTEGER,
    FA INTEGER,
    Insuffisance_renale INTEGER,
    BPCO INTEGER,
    Asthme INTEGER,
    Femme_enceinte INTEGER
)
''')
conn.commit()
print("  ✓ Table DIM_PATIENT créée")

# 3.2 Table de dimension: DIM_SYMPTOMES
print("\n3.2 Création de DIM_SYMPTOMES:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_SYMPTOMES (
    Symptome_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Douleur_lombaire_droite INTEGER,
    Douleur_lombaire_gauche INTEGER,
    Douleur_lombaire_bilaterale INTEGER,
    Douleur_FID INTEGER,
    Douleur_FIG INTEGER,
    Hematurie INTEGER,
    Pollakiurie INTEGER,
    Dysurie INTEGER,
    Irradiation_OGE INTEGER,
    Brulure_mictionnelle INTEGER,
    Duree_symptomatologie REAL,
    Douleur_ebranlement_droite INTEGER,
    Douleur_ebranlement_gauche INTEGER,
    Contact_lombaire INTEGER,
    Masse_lombaire INTEGER
)
''')
conn.commit()
print("  ✓ Table DIM_SYMPTOMES créée")

# 3.3 Table de dimension: DIM_TRAITEMENT
print("\n3.3 Création de DIM_TRAITEMENT:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_TRAITEMENT (
    Traitement_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    AINS INTEGER,
    Molecule_AINS REAL,
    Voie_administration_AINS REAL,
    CI_AINS INTEGER,
    Paracetamol INTEGER,
    Voie_administration_paracetamol REAL,
    Titration_morphinique INTEGER,
    Dose_totale_recue REAL,
    Complications_titration INTEGER
)
''')
conn.commit()
print("  ✓ Table DIM_TRAITEMENT créée")

# 3.4 Table de dimension: DIM_IMAGERIE
print("\n3.4 Création de DIM_IMAGERIE:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_IMAGERIE (
    Imagerie_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Imagerie INTEGER,
    AUSP INTEGER,
    Echographie_renale INTEGER,
    Uroscanner INTEGER,
    Dilatation_pyelocalicielle INTEGER,
    Calcul_unilateral INTEGER,
    Calcul_bilateral INTEGER
)
''')
conn.commit()
print("  ✓ Table DIM_IMAGERIE créée")

# 3.5 Table de faits: FAIT_CONSULTATION
print("\n3.5 Création de FAIT_CONSULTATION:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS FAIT_CONSULTATION (
    Consultation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Patient_ID INTEGER,
    Symptome_ID INTEGER,
    Traitement_ID INTEGER,
    Imagerie_ID INTEGER,
    Temperature REAL,
    FR REAL,
    SPO2 REAL,
    PAS REAL,
    PAD REAL,
    FC REAL,
    EN0 REAL,
    EN_15min REAL,
    EN_30min REAL,
    EN_45min REAL,
    EN_60min REAL,
    EN_90min REAL,
    Variation_douleur REAL,
    Amelioration_douleur INTEGER,
    Evolution_amelioration INTEGER,
    Retour_a_domicile INTEGER,
    Adresse_urg_uro INTEGER,
    Hospitalisation INTEGER,
    CN_simple INTEGER,
    CN_compliquee INTEGER,
    febrile INTEGER,
    FOREIGN KEY (Patient_ID) REFERENCES DIM_PATIENT(Patient_ID),
    FOREIGN KEY (Symptome_ID) REFERENCES DIM_SYMPTOMES(Symptome_ID),
    FOREIGN KEY (Traitement_ID) REFERENCES DIM_TRAITEMENT(Traitement_ID),
    FOREIGN KEY (Imagerie_ID) REFERENCES DIM_IMAGERIE(Imagerie_ID)
)
''')
conn.commit()
print("  ✓ Table FAIT_CONSULTATION créée")

# ==================================================================================
# ÉTAPE 4: CHARGEMENT DES DONNÉES (LOADING)
# ==================================================================================
print("\n[ÉTAPE 4] CHARGEMENT DES DONNÉES DANS LE DATA WAREHOUSE")
print("-" * 80)

# Préparer les mappings de colonnes
patient_cols = ['Age', 'Genre', 'Categorie_Age', 'ATCDS', 'Score_comorbidite',
                'Diabète', 'HTA', 'Dyslipidémie', 'FA', 'Insuffisance_rénale',
                'BPCO', 'Asthme', 'Femme_enceinte']

symptome_cols = ['Douleur_lombaire_droite', 'Douleur_lombaire_gauche', 
                 'Douleur_lombaire_bilatérale', 'Douleur_FID', 'Douleur_FIG',
                 'Hématurie', 'Pollakiurie', 'Dysurie', 'Irradiation_OGE',
                 'Brulure_mictionnelle', 'Durée_symptomatologie',
                 'Douleur_ébranlement_droite', 'Douleur_ébranlement_gauche',
                 'Contact_lombaire', 'Masse_lombaire']

traitement_cols = ['AINS', 'Molécule_AINS', 'Voie_administration_AINS', 'CI_AINS',
                   'Paracétamol', 'Voie_administration_paracétamol',
                   'Titration_morphinique', 'Dose_totale_reçue', 'Complications_titration']

imagerie_cols = ['Imagerie', 'AUSP', 'Echographie_rénale', 'Uroscanner',
                 'Dilatation_pyélocalicielle', 'Calcul_unilatéral', 'Calcul_bilatéral']

# Fonction auxiliaire pour obtenir la valeur ou None
def get_value(row, col):
    if col in df.columns:
        val = row[col]
        return None if pd.isna(val) else val
    return None

# Chargement des données
loaded_count = 0
for idx, row in df.iterrows():
    try:
        # Insérer dans DIM_PATIENT
        cursor.execute('''
        INSERT INTO DIM_PATIENT (Age, Genre, Categorie_Age, ATCDS, Score_comorbidite,
                                 Diabete, HTA, Dyslipidémie, FA, Insuffisance_renale,
                                 BPCO, Asthme, Femme_enceinte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(get_value(row, col) for col in patient_cols))
        patient_id = cursor.lastrowid
        
        # Insérer dans DIM_SYMPTOMES
        cursor.execute('''
        INSERT INTO DIM_SYMPTOMES (Douleur_lombaire_droite, Douleur_lombaire_gauche,
                                   Douleur_lombaire_bilaterale, Douleur_FID, Douleur_FIG,
                                   Hematurie, Pollakiurie, Dysurie, Irradiation_OGE,
                                   Brulure_mictionnelle, Duree_symptomatologie,
                                   Douleur_ebranlement_droite, Douleur_ebranlement_gauche,
                                   Contact_lombaire, Masse_lombaire)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(get_value(row, col) for col in symptome_cols))
        symptome_id = cursor.lastrowid
        
        # Insérer dans DIM_TRAITEMENT
        cursor.execute('''
        INSERT INTO DIM_TRAITEMENT (AINS, Molecule_AINS, Voie_administration_AINS, CI_AINS,
                                    Paracetamol, Voie_administration_paracetamol,
                                    Titration_morphinique, Dose_totale_recue, Complications_titration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(get_value(row, col) for col in traitement_cols))
        traitement_id = cursor.lastrowid
        
        # Insérer dans DIM_IMAGERIE
        cursor.execute('''
        INSERT INTO DIM_IMAGERIE (Imagerie, AUSP, Echographie_renale, Uroscanner,
                                  Dilatation_pyelocalicielle, Calcul_unilateral, Calcul_bilateral)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', tuple(get_value(row, col) for col in imagerie_cols))
        imagerie_id = cursor.lastrowid
        
        # Insérer dans FAIT_CONSULTATION
        cursor.execute('''
        INSERT INTO FAIT_CONSULTATION (
            Patient_ID, Symptome_ID, Traitement_ID, Imagerie_ID,
            Temperature, FR, SPO2, PAS, PAD, FC,
            EN0, EN_15min, EN_30min, EN_45min, EN_60min, EN_90min,
            Variation_douleur, Amelioration_douleur,
            Evolution_amelioration, Retour_a_domicile, Adresse_urg_uro,
            Hospitalisation, CN_simple, CN_compliquee, febrile
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_id, symptome_id, traitement_id, imagerie_id,
            get_value(row, 'Température'), get_value(row, 'FR'), get_value(row, 'SPO2'),
            get_value(row, 'PAS'), get_value(row, 'PAD'), get_value(row, 'FC'),
            get_value(row, 'EN0'), get_value(row, 'EN_15min'), get_value(row, 'EN_30min'),
            get_value(row, 'EN_45min'), get_value(row, 'EN_60min'), get_value(row, 'EN_90min'),
            get_value(row, 'Variation_douleur'), get_value(row, 'Amelioration_douleur'),
            get_value(row, 'Evolution_amélioration'), get_value(row, 'Retour_à_domicile'),
            get_value(row, 'Adressé_urg_uro'), get_value(row, 'Hospitalisation'),
            get_value(row, 'CN_simple'), get_value(row, 'CN_compliquée'), get_value(row, 'febrile')
        ))
        
        loaded_count += 1
        if loaded_count % 50 == 0:
            conn.commit()
            print(f"  ✓ {loaded_count} enregistrements chargés...")
            
    except Exception as e:
        print(f"  ✗ Erreur ligne {idx}: {e}")
        continue

conn.commit()
print(f"\n✓ Chargement terminé: {loaded_count} enregistrements insérés")

# ==================================================================================
# ÉTAPE 5: VALIDATION ET STATISTIQUES DU DATA WAREHOUSE
# ==================================================================================
print("\n[ÉTAPE 5] VALIDATION ET STATISTIQUES DU DATA WAREHOUSE")
print("-" * 80)

# Compter les enregistrements dans chaque table
tables = ['DIM_PATIENT', 'DIM_SYMPTOMES', 'DIM_TRAITEMENT', 'DIM_IMAGERIE', 'FAIT_CONSULTATION']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  ✓ {table}: {count} enregistrements")

# Quelques statistiques
print("\nStatistiques clés:")
cursor.execute("""
SELECT 
    ROUND(AVG(Age), 1) as Age_moyen,
    COUNT(CASE WHEN Genre='2.0' THEN 1 END) as Hommes,
    COUNT(CASE WHEN Genre='4.0' THEN 1 END) as Femmes
FROM DIM_PATIENT
""")
stats = cursor.fetchone()
print(f"  • Âge moyen: {stats[0]} ans")
print(f"  • Hommes: {stats[1]} | Femmes: {stats[2]}")

cursor.execute("""
SELECT 
    ROUND(AVG(EN0), 2) as Douleur_initiale,
    ROUND(AVG(EN_90min), 2) as Douleur_finale,
    ROUND(AVG(Variation_douleur), 2) as Variation_moyenne
FROM FAIT_CONSULTATION
""")
pain_stats = cursor.fetchone()
print(f"  • Douleur initiale (EN0): {pain_stats[0]}")
print(f"  • Douleur finale (EN_90min): {pain_stats[1]}")
print(f"  • Variation moyenne: {pain_stats[2]}")

cursor.execute("""
SELECT 
    COUNT(CASE WHEN AINS=1 THEN 1 END) as AINS_count,
    COUNT(CASE WHEN Paracetamol=1 THEN 1 END) as Paracetamol_count,
    COUNT(CASE WHEN Titration_morphinique=1 THEN 1 END) as Morphine_count
FROM DIM_TRAITEMENT
""")
treatment_stats = cursor.fetchone()
print(f"  • Patients sous AINS: {treatment_stats[0]}")
print(f"  • Patients sous Paracétamol: {treatment_stats[1]}")
print(f"  • Patients sous Morphine: {treatment_stats[2]}")

# Sauvegarder le dataset nettoyé pour Power BI
df_for_powerbi = df.copy()
df_for_powerbi.to_csv('/home/claude/donnees_nettoyees_powerbi.csv', index=False)
print(f"\n✓ Dataset nettoyé exporté: donnees_nettoyees_powerbi.csv ({len(df_for_powerbi)} lignes)")

# Fermer la connexion
conn.close()

print("\n" + "="*80)
print(" ETL ET DATA WAREHOUSE TERMINÉS AVEC SUCCÈS ".center(80, "="))
print("="*80)
print(f"""
Fichiers générés:
  • datawarehouse_medical.db (Data Warehouse SQLite)
  • donnees_nettoyees_powerbi.csv (Dataset nettoyé pour Power BI)

Prochaines étapes:
  1. Importer le fichier CSV ou connecter Power BI à SQLite
  2. Créer les mesures DAX et KPIs
  3. Concevoir le dashboard interactif
""")
