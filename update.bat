@echo off
REM Se déplacer dans le dossier du projet

REM Forcer le pull
echo Forçage de la mise à jour du dépôt depuis GitHub...
git fetch origin master
git reset --hard origin/master

REM Afficher un message de fin
echo Mise à jour terminée avec succès !
pause