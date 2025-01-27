:: Installer les dépendances depuis requirements.txt
@echo off
echo Installation des dépendances...
pip install -r requirements.txt

:: Vérifier si l'installation a réussi
if %errorlevel% neq 0 (
    echo Une erreur s'est produite lors de l'installation des dépendances.
    pause
    exit /b
)

