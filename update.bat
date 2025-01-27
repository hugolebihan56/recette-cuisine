@echo off
REM Se déplacer dans le dossier du projet

REM Exécuter git pull
echo Mise à jour du dépôt depuis GitHub...
git pull https://github.com/hugolebihan56/recette-cuisine.git master

REM Afficher un message de fin
echo Mise à jour terminée !
pause