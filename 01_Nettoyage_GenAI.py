# -*- coding: utf-8 -*-
"""
Notebook 1: Nettoyage et Préparation des Données GenAI
Projet BI - Analyse de l'Adoption des GenAI dans les Entreprises

Auteures: ASMA & MONIA
Module: Data Analytics & Business Intelligence
5ème année - Ingénierie Informatique
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print(" PROJET BI - ANALYSE GENAI DANS LES ENTREPRISES ".center(80, "="))
print("="*80)
print("ÉTAPE 1: CHARGEMENT ET EXPLORATION DES DONNÉES")
print("="*80)

# Charger les données
df = pd.read_csv('enterprise_genai_data.csv')

print(f"\n✓ Données chargées avec succès!")
print(f"  - Nombre de lignes: {df.shape[0]:,}")
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

# Types de données par colonne
print("\n" + "="*80)
print("COLONNES DU DATASET")
print("="*80)
for col in df.columns:
    print(f"  • {col}: {df[col].dtype}")

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
    plt.xticks(range(len(missing_df)), missing_df['Colonne'], rotation=45, ha='right')
    plt.ylabel('Pourcentage de valeurs manquantes (%)')
    plt.title('Valeurs manquantes par colonne')
    plt.tight_layout()
    plt.savefig('01_valeurs_manquantes_genai.png', dpi=300, bbox_inches='tight')
    print("\n✓ Graphique sauvegardé: 01_valeurs_manquantes_genai.png")
    plt.close()
else:
    print("  ✓ Aucune valeur manquante détectée!")

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
print("ÉTAPE 4: ANALYSE ET NETTOYAGE PAR COLONNE")
print("="*80)

# 4.1 Analyse de la colonne Country
print("\n📊 Analyse de la colonne 'Country':")
print(f"  • Valeurs uniques: {df['Country'].nunique()}")
print(f"  • Top 10 pays:\n{df['Country'].value_counts().head(10)}")

# 4.2 Analyse de la colonne Industry
print("\n📊 Analyse de la colonne 'Industry':")
print(f"  • Valeurs uniques: {df['Industry'].nunique()}")
print(f"  • Industries:\n{df['Industry'].value_counts()}")

# 4.3 Analyse de la colonne GenAI Tool
print("\n📊 Analyse de la colonne 'GenAI Tool':")
print(f"  • Valeurs uniques: {df['GenAI Tool'].nunique()}")
print(f"  • Outils GenAI:\n{df['GenAI Tool'].value_counts()}")

# 4.4 Analyse de la colonne Adoption Year
print("\n📊 Analyse de la colonne 'Adoption Year':")
print(f"  • Min: {df['Adoption Year'].min()}")
print(f"  • Max: {df['Adoption Year'].max()}")
print(f"  • Distribution:\n{df['Adoption Year'].value_counts().sort_index()}")

# 4.5 Vérification des valeurs aberrantes numériques
print("\n📊 Vérification des valeurs aberrantes:")

# Number of Employees Impacted
print(f"\n  • Number of Employees Impacted:")
print(f"    - Min: {df['Number of Employees Impacted'].min()}")
print(f"    - Max: {df['Number of Employees Impacted'].max()}")
print(f"    - Moyenne: {df['Number of Employees Impacted'].mean():.2f}")

# New Roles Created
print(f"\n  • New Roles Created:")
print(f"    - Min: {df['New Roles Created'].min()}")
print(f"    - Max: {df['New Roles Created'].max()}")
print(f"    - Moyenne: {df['New Roles Created'].mean():.2f}")

# Training Hours Provided
print(f"\n  • Training Hours Provided:")
print(f"    - Min: {df['Training Hours Provided'].min()}")
print(f"    - Max: {df['Training Hours Provided'].max()}")
print(f"    - Moyenne: {df['Training Hours Provided'].mean():.2f}")

# Productivity Change (%)
print(f"\n  • Productivity Change (%):")
print(f"    - Min: {df['Productivity Change (%)'].min():.2f}%")
print(f"    - Max: {df['Productivity Change (%)'].max():.2f}%")
print(f"    - Moyenne: {df['Productivity Change (%)'].mean():.2f}%")

# Filtrer les valeurs aberrantes (valeurs négatives impossibles)
initial_count = len(df)
df_cleaned = df[
    (df['Number of Employees Impacted'] >= 0) &
    (df['New Roles Created'] >= 0) &
    (df['Training Hours Provided'] >= 0) &
    (df['Adoption Year'] >= 2020) &
    (df['Adoption Year'] <= 2025)
].copy()

filtered_count = initial_count - len(df_cleaned)
print(f"\n✓ {filtered_count} lignes avec valeurs aberrantes supprimées")
print(f"✓ Dataset nettoyé: {len(df_cleaned):,} lignes")

print("\n" + "="*80)
print("ÉTAPE 5: FEATURE ENGINEERING")
print("="*80)

# 5.1 Catégorisation de la taille des entreprises
print("\n🔧 Création de la catégorie 'Company_Size':")
def categorize_company_size(employees):
    if employees < 5000:
        return 'Petite'
    elif employees < 10000:
        return 'Moyenne'
    elif employees < 15000:
        return 'Grande'
    else:
        return 'Très Grande'

df_cleaned['Company_Size'] = df_cleaned['Number of Employees Impacted'].apply(categorize_company_size)
print("✓ Catégories créées: Petite (<5k), Moyenne (5k-10k), Grande (10k-15k), Très Grande (>15k)")
print(df_cleaned['Company_Size'].value_counts())

# 5.2 Catégorisation du changement de productivité
print("\n🔧 Création de la catégorie 'Productivity_Impact':")
def categorize_productivity(change):
    if change < 10:
        return 'Faible'
    elif change < 20:
        return 'Modéré'
    elif change < 30:
        return 'Élevé'
    else:
        return 'Très Élevé'

df_cleaned['Productivity_Impact'] = df_cleaned['Productivity Change (%)'].apply(categorize_productivity)
print("✓ Catégories créées: Faible (<10%), Modéré (10-20%), Élevé (20-30%), Très Élevé (>30%)")
print(df_cleaned['Productivity_Impact'].value_counts())

# 5.3 Catégorisation de l'adoption (précoce vs tardive)
print("\n🔧 Création de la catégorie 'Adoption_Phase':")
def categorize_adoption(year):
    if year <= 2022:
        return 'Early Adopter'
    elif year == 2023:
        return 'Mainstream'
    else:
        return 'Late Adopter'

df_cleaned['Adoption_Phase'] = df_cleaned['Adoption Year'].apply(categorize_adoption)
print("✓ Catégories créées: Early Adopter (≤2022), Mainstream (2023), Late Adopter (≥2024)")
print(df_cleaned['Adoption_Phase'].value_counts())

# 5.4 Calcul du ratio Formation/Employés
print("\n🔧 Calcul du ratio 'Training_per_Employee':")
df_cleaned['Training_per_Employee'] = (
    df_cleaned['Training Hours Provided'] /
    (df_cleaned['Number of Employees Impacted'] + 1)  # +1 pour éviter division par zéro
)
print(f"✓ Moyenne d'heures de formation par employé: {df_cleaned['Training_per_Employee'].mean():.2f}h")

# 5.5 Calcul du ratio Nouveaux Rôles/Employés
print("\n🔧 Calcul du ratio 'New_Roles_Rate':")
df_cleaned['New_Roles_Rate'] = (
    df_cleaned['New Roles Created'] /
    (df_cleaned['Number of Employees Impacted'] + 1) * 100
)
print(f"✓ Taux moyen de création de nouveaux rôles: {df_cleaned['New_Roles_Rate'].mean():.2f}%")

# 5.6 Analyse du sentiment (extraction de mots-clés)
print("\n🔧 Analyse du sentiment 'Employee Sentiment':")
def extract_sentiment_category(sentiment):
    sentiment_lower = sentiment.lower()
    if 'anxiety' in sentiment_lower or 'concern' in sentiment_lower or 'scary' in sentiment_lower:
        return 'Négatif'
    elif 'love' in sentiment_lower or 'exciting' in sentiment_lower or 'improved' in sentiment_lower:
        return 'Positif'
    else:
        return 'Neutre'

df_cleaned['Sentiment_Category'] = df_cleaned['Employee Sentiment'].apply(extract_sentiment_category)
print("✓ Catégories de sentiment créées: Positif, Neutre, Négatif")
print(df_cleaned['Sentiment_Category'].value_counts())

print("\n" + "="*80)
print("ÉTAPE 6: VISUALISATIONS EXPLORATOIRES")
print("="*80)

# 6.1 Distribution par pays
print("\n📊 Création de la visualisation par pays...")
fig, ax = plt.subplots(figsize=(12, 6))
country_counts = df_cleaned['Country'].value_counts().head(15)
country_counts.plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Top 15 Pays avec Adoption GenAI', fontsize=14, fontweight='bold')
ax.set_xlabel('Pays')
ax.set_ylabel('Nombre d\'entreprises')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('02_distribution_pays.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 02_distribution_pays.png")
plt.close()

# 6.2 Distribution par industrie
print("\n📊 Création de la visualisation par industrie...")
fig, ax = plt.subplots(figsize=(12, 6))
industry_counts = df_cleaned['Industry'].value_counts()
industry_counts.plot(kind='barh', ax=ax, color='coral')
ax.set_title('Distribution par Secteur d\'Activité', fontsize=14, fontweight='bold')
ax.set_xlabel('Nombre d\'entreprises')
ax.set_ylabel('Secteur')
plt.tight_layout()
plt.savefig('03_distribution_industrie.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 03_distribution_industrie.png")
plt.close()

# 6.3 Distribution par outil GenAI
print("\n📊 Création de la visualisation par outil GenAI...")
fig, ax = plt.subplots(figsize=(10, 10))
genai_counts = df_cleaned['GenAI Tool'].value_counts()
colors = plt.cm.Set3(range(len(genai_counts)))
ax.pie(genai_counts, labels=genai_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
ax.set_title('Répartition des Outils GenAI', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('04_distribution_genai_tools.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 04_distribution_genai_tools.png")
plt.close()

# 6.4 Évolution de l'adoption par année
print("\n📊 Création de la visualisation de l'évolution temporelle...")
fig, ax = plt.subplots(figsize=(12, 6))
year_counts = df_cleaned['Adoption Year'].value_counts().sort_index()
ax.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, markersize=10, color='green')
ax.set_title('Évolution de l\'Adoption GenAI par Année', fontsize=14, fontweight='bold')
ax.set_xlabel('Année')
ax.set_ylabel('Nombre d\'entreprises')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('05_evolution_adoption.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 05_evolution_adoption.png")
plt.close()

# 6.5 Distribution du changement de productivité
print("\n📊 Création de la visualisation du changement de productivité...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Histogramme
ax1.hist(df_cleaned['Productivity Change (%)'], bins=30, color='purple', alpha=0.7, edgecolor='black')
ax1.set_title('Distribution du Changement de Productivité', fontsize=14, fontweight='bold')
ax1.set_xlabel('Changement de Productivité (%)')
ax1.set_ylabel('Fréquence')
ax1.axvline(df_cleaned['Productivity Change (%)'].mean(), color='red', linestyle='--', linewidth=2, label=f'Moyenne: {df_cleaned["Productivity Change (%)"].mean():.2f}%')
ax1.legend()

# Box plot
ax2.boxplot(df_cleaned['Productivity Change (%)'], vert=True)
ax2.set_title('Box Plot - Productivité', fontsize=14, fontweight='bold')
ax2.set_ylabel('Changement de Productivité (%)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('06_analyse_productivite.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 06_analyse_productivite.png")
plt.close()

# 6.6 Heatmap de corrélation
print("\n📊 Création de la matrice de corrélation...")
numeric_cols = ['Number of Employees Impacted', 'New Roles Created',
                'Training Hours Provided', 'Productivity Change (%)',
                'Training_per_Employee', 'New_Roles_Rate']
correlation_matrix = df_cleaned[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title('Matrice de Corrélation des Variables Numériques', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('07_correlation_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 07_correlation_matrix.png")
plt.close()

print("\n" + "="*80)
print("ÉTAPE 7: RÉSUMÉ FINAL ET EXPORT")
print("="*80)

print(f"\n📊 RÉSUMÉ DU NETTOYAGE:")
print(f"  - Lignes initiales: {initial_count:,}")
print(f"  - Lignes finales: {len(df_cleaned):,}")
print(f"  - Lignes supprimées: {filtered_count:,} ({filtered_count/initial_count*100:.2f}%)")
print(f"  - Colonnes initiales: {len(df.columns)}")
print(f"  - Colonnes finales: {len(df_cleaned.columns)}")
print(f"  - Nouvelles features créées: 7")

# Vérification finale des valeurs manquantes
final_missing = df_cleaned.isnull().sum().sum()
print(f"\n✓ Valeurs manquantes restantes: {final_missing}")

# Sauvegarder les données nettoyées
output_file = 'donnees_genai_nettoyees.csv'
df_cleaned.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n✅ Données nettoyées sauvegardées: {output_file}")

# Créer un rapport de nettoyage détaillé
rapport = f"""
{'='*80}
RAPPORT DE NETTOYAGE DES DONNÉES - GENAI ENTREPRISES
{'='*80}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. DONNÉES INITIALES
   - Nombre de lignes: {initial_count:,}
   - Nombre de colonnes: {len(df.columns)}
   - Taille mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB

2. NETTOYAGE EFFECTUÉ
   - Doublons supprimés: {duplicates}
   - Valeurs aberrantes filtrées: {filtered_count}
   - Valeurs manquantes traitées: {missing_df['Valeurs_Manquantes'].sum() if len(missing_df) > 0 else 0}

3. DONNÉES FINALES
   - Nombre de lignes: {len(df_cleaned):,}
   - Nombre de colonnes: {len(df_cleaned.columns)}
   - Taux de conservation: {len(df_cleaned)/initial_count*100:.2f}%
   - Valeurs manquantes: {final_missing}

4. NOUVELLES FEATURES CRÉÉES
   - Company_Size: Catégorisation de la taille d'entreprise
   - Productivity_Impact: Catégorisation de l'impact productivité
   - Adoption_Phase: Phase d'adoption (Early/Mainstream/Late)
   - Training_per_Employee: Ratio formation par employé
   - New_Roles_Rate: Taux de création de nouveaux rôles
   - Sentiment_Category: Catégorisation du sentiment employé

5. ANALYSES CLÉS
   - Nombre de pays: {df_cleaned['Country'].nunique()}
   - Nombre d'industries: {df_cleaned['Industry'].nunique()}
   - Nombre d'outils GenAI: {df_cleaned['GenAI Tool'].nunique()}
   - Années d'adoption: {df_cleaned['Adoption Year'].min()} - {df_cleaned['Adoption Year'].max()}

6. STATISTIQUES PRINCIPALES
   - Employés impactés (moyenne): {df_cleaned['Number of Employees Impacted'].mean():,.0f}
   - Nouveaux rôles créés (moyenne): {df_cleaned['New Roles Created'].mean():.2f}
   - Heures de formation (moyenne): {df_cleaned['Training Hours Provided'].mean():,.0f}h
   - Changement productivité (moyenne): {df_cleaned['Productivity Change (%)'].mean():.2f}%

7. FICHIERS GÉNÉRÉS
   - donnees_genai_nettoyees.csv
   - 01_valeurs_manquantes_genai.png (si applicable)
   - 02_distribution_pays.png
   - 03_distribution_industrie.png
   - 04_distribution_genai_tools.png
   - 05_evolution_adoption.png
   - 06_analyse_productivite.png
   - 07_correlation_matrix.png
   - rapport_nettoyage_genai.txt

{'='*80}
"""

with open('rapport_nettoyage_genai.txt', 'w', encoding='utf-8') as f:
    f.write(rapport)

print(rapport)
print("✅ Rapport de nettoyage sauvegardé: rapport_nettoyage_genai.txt")

print("\n" + "="*80)
print(" 🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS! ".center(80, "="))
print("="*80)
print("\nFichiers générés:")
print("  1. donnees_genai_nettoyees.csv - Données prêtes pour le Data Warehouse")
print("  2. rapport_nettoyage_genai.txt - Rapport détaillé")
print("  3. Graphiques d'analyse exploratoire (7 fichiers PNG)")
print("\n➡️  Prochaine étape: Créer le Data Warehouse avec modèle en étoile")
print("="*80)
