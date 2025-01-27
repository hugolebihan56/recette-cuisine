@echo off
title Menu Principal - Bot Chasseur
color 0E

:menu
color 0E
cls
echo.
echo     ___   ___   __  __   _______    ______        _______   ______   _________  
echo    /__/\ /__/\ /_/\/_/\ /______/\  /_____/\     /_______/\ /_____/\ /________/\ 
echo    \::\ \\  \ \\:\ \:\ \\::::__\/__\:::_ \ \    \::: _  \ \\:::_ \ \\__.::.__\/ 
echo     \::\/_\ .\ \\:\ \:\ \\:\ /____/\\:\ \ \ \    \::(_)  \/_\:\ \ \ \  \::\ \   
echo      \:: ___::\ \\:\ \:\ \\:\\_  _\/ \:\ \ \ \    \::  _  \ \\:\ \ \ \  \::\ \  
echo       \: \ \\::\ \\:\_\:\ \\:\_\ \ \  \:\_\ \ \    \::(_)  \ \\:\_\ \ \  \::\ \ 
echo        \__\/ \::\/ \_____\/ \_____\/   \_____\/     \_______\/ \_____\/   \__\/  v3.4
echo.
echo            === Decale la fenetre pour ne pas gener la chasse ! ===
echo.
echo [1] Nouvelle chasse (NEW !!!)
echo [2] Reprendre en plein milieu d'une chasse (Ancien bot)
echo [3] Parametrer le bot
echo [4] Installer le bot
echo [5] Indice inconnu ? Mettre a jour la base de donnees
echo [6] Quitter
echo.
set /p choix="Veuillez choisir une option (1-6) (1 par default) : "

if "%choix%"=="1" goto nouvelle_chasse
if "%choix%"=="2" goto reprendre_chasse
if "%choix%"=="3" goto parametrer_bot
if "%choix%"=="4" goto installer_bot
if "%choix%"=="5" goto update_bdd
if "%choix%"=="6" goto quitter

rem Si aucune des options valides n'est saisie, choisir 1 par défaut
echo Option invalide, lancement de la chasse par défaut !
set choix=1
goto nouvelle_chasse
pause
goto menu

:nouvelle_chasse
cls
color 0E
echo =====================================================
echo                  NOUVELLE CHASSE                    
echo =====================================================
echo.
echo Le bot commence une nouvelle chasse...
call bat/launch_bot.bat
echo.
color 0A
pause
goto menu

:reprendre_chasse
cls
color 0A
echo =====================================================
echo                  NOUVELLE CHASSE                    
echo =====================================================
echo.
echo Le bot commence une nouvelle chasse...
call python dev/main.py
echo.
color 0A
pause
goto menu

:parametrer_bot
cls
color 0B
echo =====================================================
echo                  PARAMETRAGE DU BOT                 
echo =====================================================
echo.
echo Ouverture de "parametrage.bat"...
call bat/parametrage.bat
echo.
color 0B
pause
goto menu

:installer_bot
cls
color 0C
echo =====================================================
echo                 INSTALLATION DU BOT                 
echo =====================================================
echo.
echo Lancement de l'installation...
call bat/install.bat
echo.
color 0C
pause
goto menu

:update_bdd
cls
color 0D
echo =====================================================
echo            MISE A JOUR DE LA BASE DE DONNEES         
echo =====================================================
echo.
echo Lancement de la mise a jour de la base de donnees...
python dev/update_bdd.py
echo.
color 0D
pause
goto menu

:quitter
cls
color 0F
echo Merci d'avoir utilisé le BOT CHASSEUR !
echo A bientot !
pause
exit
