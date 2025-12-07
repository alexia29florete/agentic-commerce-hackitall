@echo off
echo ==== Pornesc backend-ul FastAPI... ====

rem -> Intrăm în folderul backend
cd agentic-commerce-hackitall

rem -> Pornim uvicorn într-o fereastră separată
start cmd /k "uvicorn main:app --reload --port 8000"

cd ..

echo ==== Pornesc Live Server pentru frontend... ====
powershell -ExecutionPolicy Bypass -File start_live_server.ps1

exit
