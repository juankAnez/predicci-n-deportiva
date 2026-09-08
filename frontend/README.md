# Frontend - Predicción Deportiva

Módulo frontend para la plataforma de predicción deportiva y análisis de cuotas de valor (+EV).

## Conexión con el Backend
- **API Base URL:** `http://localhost:5000/api/v1`
- **Modo Servidor:** Iniciar con `python backend/scripts/run_server.py` o `docker-compose up api`

## Estructura Recomendada
- **Framework:** React + TypeScript + Vite o Next.js
- **Estilos:** TailwindCSS para dashboards analíticos y tablas de cuotas
- **Visualización de Datos:** Recharts o Chart.js para distribuciones Poisson, evolución de Elo y probabilidades de mercado

## Inicialización Rápida (React + Vite)
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm run dev
```