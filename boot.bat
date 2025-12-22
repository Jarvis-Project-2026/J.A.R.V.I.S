@echo off
TITLE J.A.R.V.I.S. System Boot
COLOR 0B

echo ==================================================
echo        INICIALIZANDO PROTOCOLOS J.A.R.V.I.S.
echo ==================================================
echo.

:: FORCAR O USO DA GPU NVIDIA (CUDA)
:: O índice 0 aqui se refere à primeira placa NVIDIA encontrada.
:: O CUDA ignora a Intel Graphics ou processador integrado.
:: OBS: Certifique-se de que os drivers NVIDIA e CUDA estejam corretamente 
:: instalados e que o CUDA índice 0 esteja disponível no PC e seja a placa de vídeo ativa.
set CUDA_VISIBLE_DEVICES=0

:: DESATIVAR OVERHEAD DA GPU INTEGRADA
:: Impede que o Ollama tente usar a memória compartilhada da Intel.
set OLLAMA_GPU_OVERHEAD=0

echo [SYSTEM] Variaveis de ambiente de GPU configuradas.
echo [SYSTEM] Placa Alvo: NVIDIA GeForce GTX 1650
echo.

:: ENTRAR NA PASTA DO BACKEND
cd backend

:: EXECUTAR O JARVIS
echo.
echo [BOOT] Executando main.py...
echo.
python main.py

:: Mantém a janela aberta caso dê erro
pause