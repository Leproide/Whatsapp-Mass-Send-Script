@echo off
Color A
cls

REM Whatsapp Mass Send Script
REM leproide@paranoici.org

setlocal enabledelayedexpansion

REM === Config ===
set "SCRIPT=send_whatsapp_playwright.py"
set "REQ=requirements.txt"

REM Check if this is a restart after Python installation
if "%1"=="--restart-after-python" (
    echo [INFO] Riavvio dopo installazione Python
    goto check_python_after_install
)

echo.
echo === Whatsapp Mass Send Script / Playwright bootstrapper ===
echo.

REM --- 1) Check Python presence ---
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Python non trovato nel PATH. Provo a installare tramite winget
    echo [INFO] Esegui come amministratore se winget richiede privilegi.
    winget install --id Python.Python.3 -e --silent
    if %ERRORLEVEL% neq 0 (
        echo [ERR] winget non ha installato Python. Installa Python manualmente e poi rilancia questo script.
        pause
        exit /b 1
    )
    echo [OK] Python installato. Riavvio lo script per aggiornare il PATH
    timeout /t 3 >nul
    REM Riavvio lo script con parametro di restart
    "%~f0" --restart-after-python
    exit /b 0
)

:check_python_after_install
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERR] Python ancora non disponibile nel PATH dopo il riavvio.
    echo [INFO] Prova a chiudere e riaprire il terminale oppure riavvia il PC.
    echo [INFO] Se Python è installato ma non nel PATH, modifica il PATH o avvia con il path completo a python.exe.
    pause
    exit /b 2
)

echo [OK] Python trovato:
python --version

REM --- 2) Ensure pip exists (only install if missing) ---
echo.
echo [INFO] Verifico presenza di pip
python -m pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] pip non trovato. Provo a scaricare get-pip.py con PowerShell.
    powershell -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'; exit 0 } catch { exit 1 }"
    if %ERRORLEVEL% neq 0 (
        echo [ERR] Impossibile scaricare get-pip.py. Installa pip manualmente.
        pause
        exit /b 6
    )
    echo [INFO] Eseguo get-pip.py
    python get-pip.py
    if %ERRORLEVEL% neq 0 (
        echo [ERR] Installazione pip via get-pip.py fallita.
        del /f /q get-pip.py >nul 2>&1
        pause
        exit /b 7
    )
    del /f /q get-pip.py >nul 2>&1
    echo [OK] pip installato.
) else (
    echo [OK] pip presente.
)

REM --- 3) Optionally upgrade pip/setuptools/wheel if explicitly requested ---
REM If you want to force an upgrade uncomment the following lines:
REM echo [INFO] Aggiorno pip, setuptools e wheel
REM python -m pip install --upgrade pip setuptools wheel

REM --- 4) Install dependencies ---
echo.
if exist "%REQ%" (
    echo [INFO] Trovato %REQ% - installo pacchetti da file.
    python -m pip install -r "%REQ%"
    if %ERRORLEVEL% neq 0 (
        echo [ERR] pip install -r %REQ% ha restituito errore.
        pause
        exit /b 3
    )
) else (
    echo [INFO] %REQ% non trovato. Controllo se serve 'playwright' e lo installo se mancante.

    echo [INFO] Controllo se Playwright è installato.
    python -c "import importlib.util; exit(0 if importlib.util.find_spec('playwright') else 1)" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [OK] Playwright Python presente.
    ) else (
        echo [INFO] Playwright Python non trovato. Lo installo.
        python -m pip install playwright
        if %ERRORLEVEL% neq 0 (
            echo [ERR] pip install playwright fallito.
            pause
            exit /b 4
        )
        echo [INFO] Installazione Playwright completata. Installo i browser necessari (python -m playwright install)
        python -m playwright install
        if %ERRORLEVEL% neq 0 (
            echo [WARN] 'python -m playwright install' ha restituito errore. Prova a eseguirlo manualmente: python -m playwright install
        )
    )
)

REM --- 5) Final checks and run script ---
echo.
if not exist "%SCRIPT%" (
    echo [ERR] File di avvio non trovato: %SCRIPT%
    echo [INFO] Assicurati di eseguire questo .bat nella cartella contenente %SCRIPT%.
    pause
    exit /b 5
)

echo [INFO] Tutto pronto. Avvio: %SCRIPT%
python "%SCRIPT%" %*
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [OK] Script terminato correttamente.
) else (
    echo [ERR] Script terminato con codice d'errore %RC%.
)

endlocal
exit /b %RC%