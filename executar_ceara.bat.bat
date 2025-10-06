@echo off
cd C:\APIsTransparente

REM Garantir que dependências estão corretas
C:\APIsTransparente\.venv\Scripts\pip install -r requirements.txt --quiet

REM Criar pasta de logs se não existir
if not exist "C:\APIsTransparente\logs" mkdir "C:\APIsTransparente\logs"

REM Executar notebook com Papermill (mais estável que nbconvert no Win + Py3.13)
C:\APIsTransparente\.venv\Scripts\python.exe -m papermill "C:\APIsTransparente\ceara_transparente.ipynb" "C:\APIsTransparente\logs\ceara_transparente_output.ipynb"

echo.
echo =======================================
echo Execução finalizada!
echo Saída em: C:\APIsTransparente\logs\ceara_transparente_output.ipynb
echo =======================================
pause
