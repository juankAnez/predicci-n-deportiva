@echo off
title Lanzador - Prediccion Deportiva
echo ========================================================
echo   INICIANDO SISTEMA DE PREDICCION DEPORTIVA IA
echo ========================================================
echo.

echo [1/2] Iniciando Backend Flask en http://127.0.0.1:5000...
start "Backend - Flask API (Prediccion Deportiva)" cmd /k "python backend/src/api/app.py"

echo Esperando 3 segundos a que inicie el servidor de datos...
timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Frontend Vite en http://localhost:5173...
start "Frontend - Vite React (Prediccion Deportiva)" cmd /k "cd frontend && npm run dev"

echo Esperando 2 segundos para abrir el navegador...
timeout /t 2 /nobreak >nul

echo Abriendo interfaz web...
start http://localhost:5173

echo.
echo ========================================================
echo   PROYECTO EN EJECUCION EXITOSA
echo   - API Backend: http://127.0.0.1:5000
echo   - Web App:     http://localhost:5173
echo ========================================================

