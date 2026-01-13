@echo off
echo ========================================================================
echo    PROJET BI - ANALYSE GENAI DANS LES ENTREPRISES
echo ========================================================================
echo.
echo Ce script va executer automatiquement les etapes du projet BI:
echo   1. Nettoyage et preparation des donnees
echo   2. Creation du Data Warehouse avec modele en etoile
echo.
echo Duree estimee: 5-10 minutes
echo.
pause

echo.
echo ========================================================================
echo ETAPE 1: NETTOYAGE DES DONNEES
echo ========================================================================
echo.
python 01_Nettoyage_GenAI.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: Le nettoyage des donnees a echoue.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo ETAPE 2: CREATION DU DATA WAREHOUSE
echo ========================================================================
echo.
python 02_ETL_DataWarehouse_GenAI.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La creation du Data Warehouse a echoue.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo SUCCESS - PROJET BI TERMINE
echo ========================================================================
echo.
echo Fichiers generes:
echo   - donnees_genai_nettoyees.csv
echo   - datawarehouse_genai.db
echo   - donnees_powerbi_genai.csv
echo   - Graphiques PNG (9 fichiers)
echo   - Rapports TXT
echo.
echo Prochaine etape:
echo   Ouvrir Power BI Desktop et importer donnees_powerbi_genai.csv
echo   Suivre le guide: 03_Guide_PowerBI_KPIs.md
echo.
pause
