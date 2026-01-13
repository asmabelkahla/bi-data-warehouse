# -*- coding: utf-8 -*-
"""
Notebook 1: Nettoyage et Préparation des Données
Projet BI - Analyse des Coliques Néphrétiques
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("ÉTAPE 1: CHARGEMENT DES DONNÉES")
print("="*80)

# Charger les données
df = pd.read_csv('data9.csv')

print(f"\n✓ Données chargées avec succès!")
print(f"  - Nombre de lignes: {df.shape[0]}")
print(f"  - Nombre de colonnes: {df.shape[1]}")
print(f"\nAperçu des premières lignes:")
print(df.head())

# Informations sur les données
print("\n" + "="*80)
print("INFORMATIONS SUR LES DONNÉES")
print("="*80)
print(df.info())

# Statistiques descriptives
print("\n" + "="*80)
print("STATISTIQUES DESCRIPTIVES")
print("="*80)
print(df.describe())

print("\n" + "="*80)
print("ÉTAPE 2: ANALYSE DES VALEURS MANQUANTES")
print("="*80)

# Analyse des valeurs manquantes
missing_values = df.isnull().sum()
missing_percentage = (df.isnull().sum() / len(df)) * 100
missing_df = pd.DataFrame({
    'Colonne': missing_values.index,
    'Valeurs_Manquantes': missing_values.values,
    'Pourcentage': missing_percentage.values
})
missing_df = missing_df[missing_df['Valeurs_Manquantes'] > 0].sort_values('Valeurs_Manquantes', ascending=False)

print(f"\n✓ Colonnes avec valeurs manquantes: {len(missing_df)}")
if len(missing_df) > 0:
    print("\n" + missing_df.to_string(index=False))
    
    # Visualisation
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(missing_df)), missing_df['Pourcentage'])
    plt.xticks(range(len(missing_df)), missing_df['Colonne'], rotation=90)
    plt.ylabel('Pourcentage de valeurs manquantes (%)')
    plt.title('Valeurs manquantes par colonne')
    plt.tight_layout()
    plt.savefig('01_valeurs_manquantes.png', dpi=300, bbox_inches='tight')
    print("\n✓ Graphique sauvegardé: 01_valeurs_manquantes.png")
    plt.close()

print("\n" + "="*80)
print("ÉTAPE 3: DÉTECTION DES DOUBLONS")
print("="*80)

# Vérifier les doublons
duplicates = df.duplicated().sum()
print(f"\n✓ Nombre de doublons détectés: {duplicates}")

if duplicates > 0:
    print("  Suppression des doublons...")
    df = df.drop_duplicates(keep='first')
    print(f"  ✓ Doublons supprimés. Nouvelles dimensions: {df.shape}")

print("\n" + "="*80)
print("ÉTAPE 4: GESTION DES VALEURS ABERRANTES")
print("="*80)

# Fonction pour détecter les valeurs aberrantes
def detect_outliers(data, column, lower_bound, upper_bound):
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return len(outliers), outliers

# Vérifier les plages cliniquement plausibles
print("\n🔍 Vérification des plages cliniquement plausibles:")

# Age
age_outliers, _ = detect_outliers(df, 'Age', 0, 120)
print(f"  - Age (0-120 ans): {age_outliers} valeurs aberrantes")

# Température
temp_outliers, _ = detect_outliers(df, 'Température', 34, 42)
print(f"  - Température (34-42°C): {temp_outliers} valeurs aberrantes")

# Fréquence cardiaque
fc_outliers, _ = detect_outliers(df, 'FC', 30, 220)
print(f"  - FC (30-220 bpm): {fc_outliers} valeurs aberrantes")

# Pression artérielle systolique
pas_outliers, _ = detect_outliers(df, 'PAS', 60, 250)
print(f"  - PAS (60-250 mmHg): {pas_outliers} valeurs aberrantes")

# SPO2
spo2_outliers, _ = detect_outliers(df, 'SPO2', 70, 100)
print(f"  - SPO2 (70-100%): {spo2_outliers} valeurs aberrantes")

# Filtrage des valeurs aberrantes
print("\n📊 Filtrage des valeurs aberrantes...")
df_cleaned = df[
    (df['Age'] >= 0) & (df['Age'] <= 120) &
    (df['Température'] >= 34) & (df['Température'] <= 42) &
    (df['FC'] >= 30) & (df['FC'] <= 220) &
    (df['PAS'] >= 60) & (df['PAS'] <= 250) &
    (df['SPO2'] >= 70) & (df['SPO2'] <= 100)
].copy()

print(f"  ✓ Lignes conservées: {len(df_cleaned)}/{len(df)} ({len(df_cleaned)/len(df)*100:.1f}%)")

print("\n" + "="*80)
print("ÉTAPE 5: IMPUTATION DES VALEURS MANQUANTES")
print("="*80)

# Imputation logique pour ATCDS
print("\n🔧 Imputation logique pour ATCDS:")
# Colonnes d'antécédents spécifiques
antecedent_cols = ['Diabète', 'HTA', 'Dyslipidémie', 'FA', 'Insuffisance_rénale']

# Compter les valeurs manquantes avant
atcds_missing_before = df_cleaned['ATCDS'].isnull().sum()

# Imputation basée sur les antécédents spécifiques
for idx, row in df_cleaned[df_cleaned['ATCDS'].isnull()].iterrows():
    has_antecedent = False
    for col in antecedent_cols:
        if pd.notna(row[col]) and row[col] == 2.0:  # 2 = Oui
            has_antecedent = True
            break
    
    if has_antecedent:
        df_cleaned.loc[idx, 'ATCDS'] = 2.0  # A des antécédents
    else:
        df_cleaned.loc[idx, 'ATCDS'] = 4.0  # Pas d'antécédents

atcds_missing_after = df_cleaned['ATCDS'].isnull().sum()
print(f"  ✓ ATCDS imputé: {atcds_missing_before - atcds_missing_after} valeurs")

# Imputation basée sur le genre pour Femme_enceinte
print("\n🔧 Imputation pour Femme_enceinte:")
femme_enceinte_before = df_cleaned['Femme_enceinte'].isnull().sum()

# Pour les hommes (Genre=2), mettre 4 (Non)
df_cleaned.loc[df_cleaned['Genre'] == 2.0, 'Femme_enceinte'] = df_cleaned.loc[
    df_cleaned['Genre'] == 2.0, 'Femme_enceinte'
].fillna(4.0)

# Pour les femmes (Genre=4), utiliser le mode
mode_femme = df_cleaned[df_cleaned['Genre'] == 4.0]['Femme_enceinte'].mode()[0]
df_cleaned.loc[df_cleaned['Genre'] == 4.0, 'Femme_enceinte'] = df_cleaned.loc[
    df_cleaned['Genre'] == 4.0, 'Femme_enceinte'
].fillna(mode_femme)

femme_enceinte_after = df_cleaned['Femme_enceinte'].isnull().sum()
print(f"  ✓ Femme_enceinte imputé: {femme_enceinte_before - femme_enceinte_after} valeurs")

# Imputation par mode pour les autres colonnes avec peu de valeurs manquantes
print("\n🔧 Imputation par mode pour les colonnes avec peu de valeurs manquantes:")
columns_to_impute = ['febrile', 'AUSP']

for col in columns_to_impute:
    if col in df_cleaned.columns and df_cleaned[col].isnull().sum() > 0:
        missing_before = df_cleaned[col].isnull().sum()
        mode_val = df_cleaned[col].mode()[0]
        df_cleaned[col].fillna(mode_val, inplace=True)
        print(f"  ✓ {col}: {missing_before} valeurs imputées avec mode={mode_val}")

# Supprimer la colonne Longueur_DPC si elle a trop de valeurs manquantes
if 'Longueur_DPC' in df_cleaned.columns:
    missing_pct = df_cleaned['Longueur_DPC'].isnull().sum() / len(df_cleaned) * 100
    if missing_pct > 50:
        print(f"\n⚠️  Suppression de Longueur_DPC ({missing_pct:.1f}% manquant)")
        df_cleaned = df_cleaned.drop('Longueur_DPC', axis=1)

print("\n" + "="*80)
print("ÉTAPE 6: BINARISATION DES VARIABLES")
print("="*80)

# Fonction pour binariser (2,4) -> (1,0)
def binarize_column(col_data):
    """Convertir (2,4) en (1,0) ou (4,6) en (0,1)"""
    unique_vals = col_data.dropna().unique()
    
    if set(unique_vals).issubset({2.0, 4.0}):
        return col_data.map({2.0: 1, 4.0: 0})
    elif set(unique_vals).issubset({4.0, 6.0}):
        return col_data.map({4.0: 0, 6.0: 1})
    else:
        return col_data

# Identifier et binariser les colonnes binaires
print("\n🔧 Binarisation des variables codées (2,4) ou (4,6):")
binary_count = 0

for col in df_cleaned.columns:
    if df_cleaned[col].dtype in ['float64', 'int64']:
        unique_vals = df_cleaned[col].dropna().unique()
        if len(unique_vals) == 2:
            if set(unique_vals).issubset({2.0, 4.0}) or set(unique_vals).issubset({4.0, 6.0}):
                df_cleaned[col] = binarize_column(df_cleaned[col])
                binary_count += 1

print(f"  ✓ {binary_count} colonnes binarisées")

print("\n" + "="*80)
print("ÉTAPE 7: CRÉATION DE CATÉGORIES D'ÂGE")
print("="*80)

# Créer des catégories d'âge
bins = [0, 18, 30, 50, 70, 120]
labels = ['Enfant_Ado', 'Jeune_adulte', 'Adulte', 'Senior', 'Personne_âgée']
df_cleaned['Categorie_Age'] = pd.cut(df_cleaned['Age'], bins=bins, labels=labels, right=False)

print("\n✓ Catégories d'âge créées:")
print(df_cleaned['Categorie_Age'].value_counts().sort_index())

# Visualisation
plt.figure(figsize=(10, 6))
df_cleaned['Categorie_Age'].value_counts().sort_index().plot(kind='bar', color='steelblue')
plt.title('Distribution des patients par catégorie d\'âge')
plt.xlabel('Catégorie d\'âge')
plt.ylabel('Nombre de patients')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('02_distribution_age.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 02_distribution_age.png")
plt.close()

print("\n" + "="*80)
print("ÉTAPE 8: ENGINEERING DE FEATURES - ÉVOLUTION DE LA DOULEUR")
print("="*80)

# Calculer la variation de douleur
pain_cols = ['EN0', 'EN_15min', 'EN_30min', 'EN_45min', 'EN_60min', 'EN_90min']

# Vérifier que toutes les colonnes existent
available_pain_cols = [col for col in pain_cols if col in df_cleaned.columns]
print(f"\n✓ Colonnes de douleur disponibles: {len(available_pain_cols)}/{len(pain_cols)}")

if 'EN0' in df_cleaned.columns and 'EN_90min' in df_cleaned.columns:
    # Variation de douleur
    df_cleaned['Variation_douleur'] = df_cleaned['EN_90min'] - df_cleaned['EN0']
    
    # Pourcentage de réduction de douleur
    df_cleaned['Pct_reduction_douleur'] = (
        (df_cleaned['EN0'] - df_cleaned['EN_90min']) / (df_cleaned['EN0'] + 0.001) * 100
    )
    
    print("\n✓ Nouvelles features créées:")
    print(f"  - Variation_douleur: {df_cleaned['Variation_douleur'].describe()}")
    print(f"  - Pct_reduction_douleur: {df_cleaned['Pct_reduction_douleur'].describe()}")
    
    # Visualisation de l'évolution de la douleur
    pain_data = df_cleaned[available_pain_cols].mean()
    
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(pain_data)), pain_data, marker='o', linewidth=2, markersize=8)
    plt.title('Évolution moyenne de la douleur dans le temps')
    plt.xlabel('Mesure de douleur')
    plt.ylabel('Score de douleur moyen')
    plt.xticks(range(len(pain_data)), [col.replace('EN_', '').replace('EN0', '0min') for col in available_pain_cols], rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('03_evolution_douleur.png', dpi=300, bbox_inches='tight')
    print("✓ Graphique sauvegardé: 03_evolution_douleur.png")
    plt.close()

print("\n" + "="*80)
print("ÉTAPE 9: NORMALISATION DES DONNÉES")
print("="*80)

# Identifier les colonnes numériques à normaliser
from sklearn.preprocessing import MinMaxScaler

# Colonnes à exclure de la normalisation
exclude_cols = ['Age', 'PAS', 'PAD', 'FC', 'Température'] + pain_cols + ['Variation_douleur', 'Pct_reduction_douleur']

# Colonnes numériques à normaliser
numeric_cols = df_cleaned.select_dtypes(include=['float64', 'int64']).columns
cols_to_normalize = [col for col in numeric_cols if col not in exclude_cols and df_cleaned[col].nunique() > 2]

if len(cols_to_normalize) > 0:
    print(f"\n✓ Normalisation de {len(cols_to_normalize)} colonnes numériques")
    scaler = MinMaxScaler()
    df_cleaned[cols_to_normalize] = scaler.fit_transform(df_cleaned[cols_to_normalize])
    print("  ✓ Normalisation terminée (échelle 0-1)")
else:
    print("\n  ℹ️  Pas de colonnes à normaliser")

print("\n" + "="*80)
print("ÉTAPE 10: RÉSUMÉ FINAL ET EXPORT")
print("="*80)

print(f"\n📊 RÉSUMÉ DU NETTOYAGE:")
print(f"  - Lignes initiales: {len(df)}")
print(f"  - Lignes finales: {len(df_cleaned)}")
print(f"  - Lignes supprimées: {len(df) - len(df_cleaned)} ({(len(df) - len(df_cleaned))/len(df)*100:.1f}%)")
print(f"  - Colonnes initiales: {len(df.columns)}")
print(f"  - Colonnes finales: {len(df_cleaned.columns)}")

# Vérification finale des valeurs manquantes
final_missing = df_cleaned.isnull().sum().sum()
print(f"\n✓ Valeurs manquantes restantes: {final_missing}")

# Sauvegarder les données nettoyées
output_file = 'donnees_nettoyees.csv'
df_cleaned.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n✅ Données nettoyées sauvegardées: {output_file}")

# Créer un rapport de nettoyage
rapport = f"""
RAPPORT DE NETTOYAGE DES DONNÉES
================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. DONNÉES INITIALES
   - Nombre de lignes: {len(df)}
   - Nombre de colonnes: {len(df.columns)}
   - Taille mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB

2. NETTOYAGE EFFECTUÉ
   - Doublons supprimés: {duplicates}
   - Valeurs aberrantes filtrées: {len(df) - len(df_cleaned)}
   - Colonnes supprimées: {len(df.columns) - len(df_cleaned.columns)}
   - Variables binarisées: {binary_count}

3. DONNÉES FINALES
   - Nombre de lignes: {len(df_cleaned)}
   - Nombre de colonnes: {len(df_cleaned.columns)}
   - Taux de conservation: {len(df_cleaned)/len(df)*100:.1f}%
   - Valeurs manquantes: {final_missing}

4. NOUVELLES FEATURES
   - Categorie_Age
   - Variation_douleur
   - Pct_reduction_douleur

5. FICHIERS GÉNÉRÉS
   - donnees_nettoyees.csv
   - 01_valeurs_manquantes.png
   - 02_distribution_age.png
   - 03_evolution_douleur.png
   - rapport_nettoyage.txt
"""

with open('rapport_nettoyage.txt', 'w', encoding='utf-8') as f:
    f.write(rapport)

print(rapport)
print("\n✅ Rapport de nettoyage sauvegardé: rapport_nettoyage.txt")
print("\n" + "="*80)
print("🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS!")
print("="*80)
print("\nFichiers générés:")
print("  1. donnees_nettoyees.csv - Données prêtes pour le Data Warehouse")
print("  2. rapport_nettoyage.txt - Rapport détaillé")
print("  3. 01_valeurs_manquantes.png - Graphique des valeurs manquantes")
print("  4. 02_distribution_age.png - Distribution par âge")
print("  5. 03_evolution_douleur.png - Évolution de la douleur")
print("\n➡️  Prochaine étape: Créer le Data Warehouse avec SQLite3")
