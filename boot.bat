@echo off
TITLE J.A.R.V.I.S. System Boot
COLOR 0B

echo ==================================================
echo        INICIALIZANDO PROTOCOLOS J.A.R.V.I.S.
echo ==================================================
echo.

:: 1. FORCAR O USO DA GPU NVIDIA (CUDA)
:: O índice 0 aqui se refere à primeira placa NVIDIA encontrada.
:: O CUDA ignora a Intel Graphics, então a GTX 1650 será a "0".
set CUDA_VISIBLE_DEVICES=0

:: 2. DESATIVAR OVERHEAD DA GPU INTEGRADA
:: Impede que o Ollama tente usar a memória compartilhada da Intel.
set OLLAMA_GPU_OVERHEAD=0

echo [SYSTEM] Variaveis de ambiente de GPU configuradas.
echo [SYSTEM] Placa Alvo: NVIDIA GeForce GTX 1650
echo.

:: 3. ENTRAR NA PASTA DO BACKEND
cd backend

:: 5. EXECUTAR O JARVIS
echo.
echo [BOOT] Executando main.py...
echo.
python main.py

:: Mantém a janela aberta caso dê erro
pause