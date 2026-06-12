# PROYECTO: PLATAFORMA PROFESIONAL DE PREDICCIÓN DEPORTIVA (FÚTBOL)

## Documento de Arquitectura Completa

---

# ÍNDICE

1. [VISIÓN GENERAL](#1-visión-general)
2. [ARQUITECTURA DEL SISTEMA](#2-arquitectura-del-sistema)
3. [ESTRUCTURA DE CARPETAS](#3-estructura-de-carpetas)
4. [TECNOLOGÍAS SELECCIONADAS](#4-tecnologías-seleccionadas)
5. [FLUJO DE DATOS](#5-flujo-de-datos)
6. [ESTRATEGIA DE SCRAPING](#6-estrategia-de-scraping)
7. [ESTRATEGIA DE ENTRENAMIENTO](#7-estrategia-de-entrenamiento)
8. [MODELOS DE PREDICCIÓN](#8-modelos-de-predicción)
9. [VARIABLES Y FEATURE ENGINEERING](#9-variables-y-feature-engineering)
10. [ESQUEMA DE BASE DE DATOS](#10-esquema-de-base-de-datos)
11. [MÉTRICAS AVANZADAS](#11-métricas-avanzadas)
12. [API Y SERVICIOS](#12-api-y-servicios)
13. [FRONTEND Y DASHBOARD](#13-frontend-y-dashboard)
14. [DEVOPS E INFRAESTRUCTURA](#14-devops-e-infraestructura)
15. [JUSTIFICACIÓN TÉCNICA](#15-justificación-técnica)
16. [RIESGOS Y LIMITACIONES](#16-riesgos-y-limitaciones)
17. [MEJORAS FUTURAS](#17-mejoras-futuras)

---

# 1. VISIÓN GENERAL

## 1.1 Propósito

Construir una plataforma profesional de análisis y predicción de partidos de fútbol que genere estimaciones probabilísticas precisas utilizando ciencia de datos, machine learning, modelos estadísticos y análisis histórico masivo.

## 1.2 Alcance Inicial

- Torneo: Mundial de Fútbol (FIFA World Cup)
- Cobertura: Todos los partidos desde 1930 hasta la actualidad
- Predicciones en tiempo real durante torneos activos

## 1.3 Alcance Futuro

- Ligas domésticas (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- Torneos continentales (Champions League, Copa Libertadores, Eurocopa, Copa América)
- Ligas secundarias y torneos menores

## 1.4 Capacidades del Sistema

| Capacidad | Descripción |
|-----------|-------------|
| Predicción de resultado | Probabilidades: Local, Empate, Visitante |
| Marcador exacto | Score más probable con probabilidad asociada |
| Predicción de goles | xG por equipo, total, over/under |
| Estadísticas avanzadas | Corners, tiros, faltas, tarjetas, posesión, pases |
| Predicción contextual | Peso del partido, fase, presión, historial |
| Explicabilidad | SHAP, feature importance, interpretación detallada |
| Actualización automática | ETL programado para datos frescos |
| Dashboard profesional | Visualización interactiva de predicciones |

---

# 2. ARQUITECTURA DEL SISTEMA

## 2.1 Diagrama de Arquitectura (Conceptual)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CAPA DE EXTRACCIÓN                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ APIs     │  │ Scrapy   │  │ Selenium │  │ Archivos          │  │
│  │ Oficiales│  │ Spiders  │  │ (fallback)│  │ Estáticos/CSV     │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       └──────────────┴──────────────┴─────────────────┘             │
│                              │                                      │
│                              ▼                                      │
│                      ┌──────────────┐                              │
│                      │  Scraping    │                              │
│                      │  Manager     │                              │
│                      └──────┬───────┘                              │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE ETL                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Pipeline ETL (Apache Airflow / APScheduler)                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │  │
│  │  │Extract   │→ │Transform │→ │Validate  │→ │Load         │  │  │
│  │  │(datos    │  │(limpieza │  │(calidad  │  │(PostgreSQL) │  │  │
│  │  │ crudos)  │  │ feature) │  │ datos)   │  │             │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CAPA DE ALMACENAMIENTO                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL                                 │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐ │  │
│  │  │Teams │ │Players│ │Match │ │Comp. │ │Rank  │ │Predict. │ │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘ │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐ │  │
│  │  │Stats │ │Inj.  │ │Susp. │ │Scrap.│ │Models│ │Cache     │ │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAPA DE FEATURE ENGINEERING                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │
│  │Variables │ │Variables │ │Variables │ │Variables │ │Variables│  │
│  │Históricas│ │Derivadas  │ │Contexto  │ │Avanzadas │ │Dinámicas│  │
│  │(raw)     │ │(stats)   │ │(peso     │ │(xG, PPDA)│ │(Elo     │  │
│  │          │ │          │ │ partido) │ │          │ │tiempo   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘  │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAPA DE MODELOS                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │
│  │ Poisson  │ │ XGBoost  │ │ LightGBM │ │  Random  │ │ Neural  │  │
│  │ (goles)  │ │(resultado)│ │(stats    │ │  Forest  │ │ Network │  │
│  │          │ │          │ │ avanzadas)│ │(benchmark)│ │(si mejora)│
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘  │
│       │            │            │            │            │          │
│       └────────────┴────────────┴────────────┴────────────┘          │
│                              │                                       │
│                      ┌──────────────┐                              │
│                      │   Ensamble   │                              │
│                      │   Stacking   │                              │
│                      └──────┬───────┘                              │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE EXPLICABILIDAD                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │ SHAP     │ │ Feature  │ │ Partial │ │ Reporte              │  │
│  │ Values   │ │Importance│ │ Dependence│ │ Interpretación       │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CAPA DE API                                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Flask REST API                                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │/predict  │ │/matches  │ │/teams    │ │/explain      │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │/players  │ │/rankings │ │/stats    │ │/models       │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAPA DE FRONTEND                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Dashboard Web (Bootstrap 5 + Chart.js)             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │Predicción│ │Gráficos  │ │Comparativa│ │Historial     │   │  │
│  │  │Principal │ │Interact. │ │Equipos   │ │Partidos      │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │Variables │ │SHAP      │ │ Ranking  │ │Gestión       │   │  │
│  │  │Influyent.│ │Force Plot│ │Dinámico  │ │Scraping      │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## 2.2 Principios Arquitectónicos

1. **Separación de responsabilidades**: Cada capa tiene una función específica y bien definida
2. **Modularidad**: Todos los componentes son intercambiables y extensibles
3. **Escalabilidad horizontal**: Diseñado para crecer con millones de registros
4. **Tolerancia a fallos**: Fallos en scraping no detienen el sistema
5. **Reproducibilidad**: Modelos versionados con semillas fijas y dependencias controladas
6. **Observabilidad**: Logs estructurados y monitoreo de todas las operaciones

---

# 3. ESTRUCTURA DE CARPETAS

```
prediccion-deportiva/
│
├── PROYECTO_ARQUITECTURA.md         ← Este documento
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.worker
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              ← Configuración centralizada
│   │   └── constants.py             ← Constantes del dominio
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   ├── match.py
│   │   │   ├── competition.py
│   │   │   └── prediction.py
│   │   └── value_objects/
│   │       ├── __init__.py
│   │       ├── ranking.py
│   │       ├── stats.py
│   │       └── probability.py
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py        ← Conexión PostgreSQL
│   │   │   ├── models/              ← Modelos SQLAlchemy
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── team.py
│   │   │   │   ├── player.py
│   │   │   │   ├── match.py
│   │   │   │   ├── competition.py
│   │   │   │   ├── ranking.py
│   │   │   │   ├── team_stats.py
│   │   │   │   ├── player_stats.py
│   │   │   │   ├── injury.py
│   │   │   │   ├── suspension.py
│   │   │   │   ├── prediction.py
│   │   │   │   ├── model_version.py
│   │   │   │   └── scraping_log.py
│   │   │   ├── migrations/          ← Migraciones Alembic
│   │   │   │   ├── env.py
│   │   │   │   ├── alembic.ini
│   │   │   │   └── versions/
│   │   │   └── repositories/        ← Repositorios
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── team_repository.py
│   │   │       ├── player_repository.py
│   │   │       ├── match_repository.py
│   │   │       ├── competition_repository.py
│   │   │       ├── ranking_repository.py
│   │   │       ├── prediction_repository.py
│   │   │       └── stats_repository.py
│   │   │
│   │   ├── scraping/
│   │   │   ├── __init__.py
│   │   │   ├── base_spider.py
│   │   │   ├── scrapers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── fifa_ranking_spider.py
│   │   │   │   ├── elo_ranking_spider.py
│   │   │   │   ├── match_results_spider.py
│   │   │   │   ├── player_stats_spider.py
│   │   │   │   ├── team_stats_spider.py
│   │   │   │   ├── injuries_spider.py
│   │   │   │   ├── transfermarkt_spider.py
│   │   │   │   ├── understat_spider.py       ← xG, xA
│   │   │   │   └── weather_spider.py
│   │   │   ├── middleware.py
│   │   │   ├── pipelines.py
│   │   │   └── settings.py
│   │   │
│   │   └── cache/
│   │       ├── __init__.py
│   │       └── redis_cache.py
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── prediction_service.py   ← Orquestador de predicciones
│   │   │   ├── match_service.py
│   │   │   ├── team_service.py
│   │   │   ├── player_service.py
│   │   │   ├── ranking_service.py
│   │   │   ├── scraping_service.py
│   │   │   ├── feature_service.py      ← Feature engineering
│   │   │   └── explainability_service.py ← SHAP + interpretación
│   │   │
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── predict_match.py
│   │   │   ├── train_models.py
│   │   │   ├── update_data.py
│   │   │   └── evaluate_models.py
│   │   │
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       ├── team_repository_interface.py
│   │       ├── player_repository_interface.py
│   │       ├── match_repository_interface.py
│   │       └── prediction_repository_interface.py
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── features/
│   │   │   ├── __init__.py
│   │   │   ├── base_features.py
│   │   │   ├── historical_features.py
│   │   │   ├── ranking_features.py
│   │   │   ├── form_features.py
│   │   │   ├── contextual_features.py
│   │   │   ├── advanced_metrics.py      ← xG, PPDA, etc.
│   │   │   ├── elo_features.py
│   │   │   └── feature_pipeline.py      ← Pipeline completo
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base_model.py
│   │   │   ├── poisson_model.py         ← Modelo 1: Poisson
│   │   │   ├── xgboost_model.py         ← Modelo 2: XGBoost
│   │   │   ├── lightgbm_model.py        ← Modelo 3: LightGBM
│   │   │   ├── random_forest_model.py   ← Modelo 4: Random Forest
│   │   │   ├── neural_network_model.py  ← Modelo 5: Neural Network
│   │   │   └── ensemble_model.py        ← Ensemble híbrido
│   │   │
│   │   ├── training/
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py
│   │   │   ├── hyperparameter_tuning.py
│   │   │   ├── cross_validation.py
│   │   │   └── backtesting.py
│   │   │
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py
│   │   │   ├── model_comparator.py
│   │   │   └── calibration.py
│   │   │
│   │   └── explainability/
│   │       ├── __init__.py
│   │       ├── shap_explainer.py
│   │       ├── feature_importance.py
│   │       └── report_generator.py
│   │
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── extractors/
│   │   │   ├── __init__.py
│   │   │   ├── api_extractor.py
│   │   │   ├── csv_extractor.py
│   │   │   └── db_extractor.py
│   │   ├── transformers/
│   │   │   ├── __init__.py
│   │   │   ├── data_cleaner.py
│   │   │   ├── stats_calculator.py
│   │   │   └── normalizer.py
│   │   ├── loaders/
│   │   │   ├── __init__.py
│   │   │   └── db_loader.py
│   │   └── pipelines/
│   │       ├── __init__.py
│   │       ├── ranking_pipeline.py
│   │       ├── matches_pipeline.py
│   │       ├── stats_pipeline.py
│   │       └── full_update_pipeline.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py                       ← Factory Flask
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── prediction_routes.py
│   │   │   ├── match_routes.py
│   │   │   ├── team_routes.py
│   │   │   ├── player_routes.py
│   │   │   ├── ranking_routes.py
│   │   │   ├── stats_routes.py
│   │   │   ├── scraping_routes.py
│   │   │   └── model_routes.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py
│   │   │   ├── rate_limiter.py
│   │   │   └── request_logger.py
│   │   ├── schemas/                     ← Pydantic validación
│   │   │   ├── __init__.py
│   │   │   ├── prediction_schema.py
│   │   │   ├── match_schema.py
│   │   │   ├── team_schema.py
│   │   │   └── player_schema.py
│   │   └── templates/
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── prediction.html
│   │       ├── dashboard.html
│   │       ├── compare.html
│   │       └── admin.html
│   │
│   └── static/
│       ├── css/
│       │   ├── style.css
│       │   └── dashboard.css
│       ├── js/
│       │   ├── main.js
│       │   ├── charts.js
│       │   ├── prediction.js
│       │   └── dashboard.js
│       └── img/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_domain.py
│   │   ├── test_features.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_database.py
│   │   ├── test_api.py
│   │   └── test_scraping.py
│   └── fixtures/
│       ├── teams.csv
│       ├── matches.csv
│       └── rankings.csv
│
├── scripts/
│   ├── init_db.py
│   ├── run_scraping.py
│   ├── train_models.py
│   ├── run_prediction.py
│   ├── evaluate_models.py
│   ├── export_data.py
│   └── seed_data.py
│
├── data/
│   ├── raw/                             ← Datos sin procesar
│   ├── processed/                       ← Datos procesados
│   ├── models/                          ← Modelos serializados
│   └── exports/                         ← Exportaciones
│
└── infra/
    ├── postgres/
    │   └── init.sql
    ├── nginx/
    │   └── default.conf
    └── monitoring/
        └── prometheus.yml
```

---

# 4. TECNOLOGÍAS SELECCIONADAS

## 4.1 Stack Principal

| Tecnología | Versión | Propósito | Justificación |
|-----------|---------|-----------|---------------|
| **Python** | 3.11+ | Lenguaje principal | Ecosistema ML/data science maduro. Tipado con mypy. |
| **PostgreSQL** | 16 | Base de datos relacional | Soporte JSON, índices parciales, extensiones estadísticas. Mejor que MySQL para consultas analíticas complejas. |
| **Flask** | 3.0+ | API REST | Ligero, flexible, amplia comunidad. FastAPI alternativo pero Flask tiene mejor integración con templates HTML para el dashboard. |
| **SQLAlchemy** | 2.0+ | ORM | Estándar de facto en Python. Soporte asíncrono, migraciones con Alembic. |
| **Pandas** | 2.1+ | Manipulación de datos | Indispensable para ETL y feature engineering. |
| **NumPy** | 1.26+ | Cálculo numérico | Base de todo el stack científico. |
| **Scikit-learn** | 1.3+ | ML base, métricas, CV | Estandarizado, fiable, necesario para preprocesamiento y evaluación. |
| **XGBoost** | 2.0+ | Modelo principal resultado | Mejor rendimiento que gradient boosting tradicional en datos tabulares. Maneja missing values nativamente. |
| **LightGBM** | 4.0+ | Estadísticas avanzadas | Más rápido que XGBoost en datasets grandes. Mejor para features categóricas. |
| **TensorFlow/PyTorch** | 2.14+/2.1+ | Red neuronal (opcional) | Solo si demuestra mejora significativa. |
| **SHAP** | 0.44+ | Explicabilidad | Única librería que proporciona explicaciones consistentes y teóricamente fundamentadas. |
| **Scrapy** | 2.11+ | Web scraping | Framework completo y robusto. Middleware para rotación de proxies, respeto de robots.txt. |
| **BeautifulSoup** | 4.12+ | HTML parsing | Ligero para tareas simples de scraping. |
| **Alembic** | 1.12+ | Migraciones DB | Estándar con SQLAlchemy. Versionado de esquema. |
| **APScheduler** | 3.10+ | ETL scheduler | Más ligero que Airflow para este alcance. Suficiente para ETL programados. |
| **Redis** | 7.0+ | Caché | Acelera consultas repetitivas. Reduce carga en DB. |
| **Celery** | 5.3+ | Tareas asíncronas | Scraping y entrenamiento en background. |
| **Gunicorn** | 21.2+ | WSGI server | Producción. Manejo de workers. |
| **Bootstrap 5** | 5.3+ | Frontend framework | Dashboard responsive, componentes modernos. |
| **Chart.js** | 4.4+ | Visualización | Gráficos interactivos, rápida integración. |
| **Docker** | 24+ | Contenedores | Entorno reproducible. |
| **Docker Compose** | 2.20+ | Orquestación local | Múltiples servicios coordinados. |

## 4.2 Por qué NO usar otras tecnologías

| Tecnología | Razón de exclusión |
|-----------|-------------------|
| **FastAPI** | Excelente para APIs, pero Flask ofrece mejor integración con Jinja2 templates para el dashboard. Si el frontend fuera SPA separado (React), FastAPI sería la elección. |
| **Apache Airflow** | Sobredimensionado para este proyecto. APScheduler + Celery cubren las necesidades ETL con mucha menor complejidad operativa. |
| **MongoDB** | Los datos son altamente relacionales. PostgreSQL con JSONB ofrece flexibilidad documental cuando se necesita, sin perder joins. |
| **React/Angular/Vue** | Añaden complejidad innecesaria. El dashboard es server-side rendering con Bootstrap 5 + Chart.js. Suficiente para paneles analíticos. |
| **Spark** | No hay volumen de datos masivo (millones de registros, no miles de millones). Pandas + chunks es suficiente. |

---

# 5. FLUJO DE DATOS

## 5.1 Flujo General

```
[Fuentes Externas]
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                  1. EXTRACCIÓN (Scraping)                     │
│                                                              │
│  Diariamente:                                                 │
│  ├── Rankings FIFA → fifa.com                                 │
│  ├── Rankings Elo → eloratings.net                           │
│  ├── Resultados recientes → soccerway.com / flashscore.com   │
│  ├── Estadísticas jugadores → transfermarkt.com              │
│  ├── xG/xA → understat.com                                   │
│  ├── Lesiones/Suspensiones → premierinjuries.com / varias    │
│  └── Condiciones climáticas → weatherapi.com                 │
│                                                              │
│  Semanalmente:                                                │
│  ├── Estadísticas avanzadas → whoscored.com                  │
│  └── Datos de partidos completos → football-data.org         │
│                                                              │
│  Mensualmente:                                                │
│  └── Actualización completa de plantillas                    │
└───────────────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  2. TRANSFORMACIÓN (ETL)                      │
│                                                              │
│  ├── Limpieza: valores nulos, outliers, normalización        │
│  ├── Feature Engineering: ~200+ variables derivadas          │
│  ├── Cálculo de métricas avanzadas: xG, PPDA, Elo dinámico  │
│  ├── Validación: reglas de negocio, integridad referencial   │
│  └── Enriquecimiento: cruce con datos históricos             │
└───────────────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  3. CARGA (PostgreSQL)                        │
│                                                              │
│  Tablas normalizadas con índices optimizados:                │
│  ├── teams, players, matches, competitions                   │
│  ├── rankings (FIFA + Elo históricos)                       │
│  ├── team_stats, player_stats                                │
│  ├── injuries, suspensions                                   │
│  └── predictions, model_versions, scraping_logs              │
└───────────────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  4. FEATURE PIPELINE                          │
│                                                              │
│  Consulta → Transformación → Feature Store (cache)           │
│                                                              │
│  ├── Features históricas (ventanas: 5, 10, 20 partidos)     │
│  ├── Features de ranking (diferencias, tendencias)           │
│  ├── Features de forma (rachas, rendimiento reciente)        │
│  ├── Features contextuales (fase, importancia, sede)         │
│  ├── Features avanzadas (xG, PPDA, Elo, presión)            │
│  └── Features de enfrentamiento directo (H2H)                │
└───────────────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  5. ENTRENAMIENTO                             │
│                                                              │
│  Pipeline de entrenamiento con validación:                   │
│  ├── Train/Test Split (80/20 temporal)                      │
│  ├── K-Fold Cross Validation (5 folds)                      │
│  ├── Backtesting histórico (por año)                        │
│  ├── Hyperparameter tuning (Optuna/GridSearch)              │
│  └── Modelos serializados → data/models/                    │
└───────────────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  6. PREDICCIÓN                                │
│                                                              │
│  ├── Cargar features del partido a predecir                  │
│  ├── Ejecutar ensemble de modelos                            │
│  ├── Generar explicación (SHAP)                              │
│  ├── Almacenar predicción en BD                              │
│  └── Servir via API + Dashboard                              │
└──────────────────────────────────────────────────────────────┘
```

## 5.2 Programación de Tareas ETL

| Tarea | Frecuencia | Prioridad | Dependencia |
|-------|-----------|-----------|-------------|
| Rankings FIFA | Diaria (si hay cambios) | Alta | - |
| Rankings Elo | Semanal | Alta | Rankings FIFA |
| Resultados partidos | Diaria | Alta | Rankings |
| Estadísticas jugadores | Semanal | Media | Equipos |
| Datos xG/xA | Semanal | Alta | Partidos |
| Lesiones | Diaria | Alta | Jugadores |
| Suspensiones | Diaria | Alta | Jugadores |
| Condiciones clima | Según partido | Media | Partidos |
| Feature engineering | Después de cada carga | Alta | Datos cargados |
| Reentrenamiento modelos | Mensual | Media | Features |
| Limpieza BD | Semanal | Baja | - |

---

# 6. ESTRATEGIA DE SCRAPING

## 6.1 Fuentes de Datos por Prioridad

### Prioridad Alta (APIs oficiales)

| API | Datos | Límites | Costo |
|-----|-------|---------|-------|
| **FIFA World Cup API** | Resultados, grupos, estadísticas | 100 req/min | Gratuita |
| **Football-data.org** | Partidos, standings, scorers | 10 req/min (free), 50 (paid) | Free tier disponible |
| **OpenLigaDB** | Partidos históricos alemanes | Sin límite | Gratuita |
| **API-Sports** | Cobertura global, estadísticas | 100 req/día (free) | Freemium |

### Prioridad Media (Web Scraping estructurado)

| Sitio | Datos | Estrategia |
|-------|-------|------------|
| **Transfermarkt** | Valor mercado, lesiones, minutos | Scrapy + rotación User-Agent |
| **Understat** | xG, xA, mapas de calor | Scrapy + BeautifulSoup |
| **WhoScored** | Estadísticas avanzadas partido | Scrapy + selenium (fallback) |
| **Soccerway** | Resultados, alineaciones | Scrapy |
| **FBref** | Estadísticas completas | Scrapy (soportan scraping explícitamente) |

### Prioridad Baja (Scraping bajo demanda)

| Sitio | Datos | Estrategia |
|-------|-------|------------|
| **Flashscore** | Tiempo real | Selenium + WebSocket |
| **ESPN FC** | Noticias, contexto | BeautifulSoup |
| **Weather API** | Clima partido | API REST gratuita |

## 6.2 Arquitectura de Scraping

```
┌─────────────────────────────────────────────────┐
│              Scraping Manager                    │
│  ┌───────────────────────────────────────────┐  │
│  │  Job Queue (Redis + Celery)               │  │
│  │  ├── Prioridad: ranking_jobs              │  │
│  │  ├── Prioridad: match_jobs               │  │
│  │  ├── Prioridad: player_jobs              │  │
│  │  └── Prioridad: stats_jobs               │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
┌─────────┐    ┌─────────────┐    ┌──────────┐
│ Spiders │    │ API Clients │    │ Parsers  │
│ Scrapy  │    │ requests    │    │ BS4/html │
└────┬────┘    └──────┬──────┘    └─────┬────┘
     │                │                 │
     └────────────────┼─────────────────┘
                      ▼
            ┌──────────────────┐
            │  Data Validator  │
            │  (Pydantic)      │
            └───────┬──────────┘
                    ▼
            ┌──────────────────┐
            │  Load → DB       │
            └──────────────────┘
```

## 6.3 Políticas de Scraping

1. **Respetar robots.txt**: Verificar siempre antes de scrapear
2. **Rate Limiting**: Máximo 1 request cada 2 segundos por dominio
3. **Rotación de User-Agent**: Pool de 50+ user agents reales
4. **Proxy Rotación**: Para sitios con bloqueo agresivo
5. **Cache HTTP**: Evitar descargas repetidas con caché local
6. **Retry con Backoff Exponencial**: 3 reintentos con espera progresiva
7. **Validación de Datos**: Esquemas Pydantic antes de insertar
8. **Logging**: Cada scraping registra éxito/fallo + tiempo + volumen

## 6.4 Manejo de Fallos

- Si una fuente falla, el sistema intenta fuentes alternativas
- Si todas fallan, se usan datos históricos extrapolados
- Alertas por email/console cuando la tasa de fallo supera 20%

---

# 7. ESTRATEGIA DE ENTRENAMIENTO

## 7.1 Pipeline de Entrenamiento

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TRAINING PIPELINE                           │
│                                                                     │
│  Fase 1: Preparación                                                │
│  ├── Cargar datos históricos completos (1930 → presente)           │
│  ├── Generar feature matrix (~200 columnas)                        │
│  ├── Split temporal: Train (80%), Test (20%)                       │
│  └── Estandarización / Normalización                               │
│                                                                     │
│  Fase 2: Validación Cruzada                                         │
│  ├── 5-Fold Cross Validation (estratificado por competición)       │
│  └── Backtesting por año (2010, 2014, 2018, 2022 para test ciego) │
│                                                                     │
│  Fase 3: Entrenamiento por Modelo                                   │
│  ├── Poisson: MLE con ventana histórica adaptativa                 │
│  ├── XGBoost: Hyperparameter tuning con Optuna                    │
│  ├── LightGBM: Optimización de leaves y learning rate              │
│  ├── Random Forest: Baseline con n_estimators=500                  │
│  └── Neural Network: MLP con 3 capas (si mejora >1% F1)           │
│                                                                     │
│  Fase 4: Ensemble                                                   │
│  ├── Stacking con LogisticRegression como meta-learner             │
│  ├── Weighted average (pesos según validación)                     │
│  └── Calibration (Platt Scaling / Isotonic)                        │
│                                                                     │
│  Fase 5: Evaluación                                                 │
│  ├── Métricas: Accuracy, Precision, Recall, F1, ROC-AUC           │
│  ├── Log Loss, Brier Score                                         │
│  ├── Matriz de confusión                                           │
│  └── Curvas de calibración                                         │
│                                                                     │
│  Fase 6: Explicabilidad                                             │
│  ├── SHAP values para cada modelo                                  │
│  ├── Feature importance agregada                                   │
│  └── Generar reporte de interpretación                             │
└─────────────────────────────────────────────────────────────────────┘
```

## 7.2 Hiperparámetros (Configuración Inicial)

### XGBoost
```python
{
    'n_estimators': 1000,
    'max_depth': 6,
    'learning_rate': 0.01,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'gamma': 0.1,
    'reg_lambda': 1.0,
    'reg_alpha': 0.1,
    'scale_pos_weight': 'balanced',
    'early_stopping_rounds': 50,
    'eval_metric': ['logloss', 'mlogloss', 'auc']
}
```

### LightGBM
```python
{
    'n_estimators': 1000,
    'max_depth': -1,
    'num_leaves': 31,
    'learning_rate': 0.01,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_lambda': 0.1,
    'reg_alpha': 0.1,
    'min_child_samples': 20,
    'cat_smooth': 10,
    'early_stopping_rounds': 50
}
```

### Random Forest (Benchmark)
```python
{
    'n_estimators': 500,
    'max_depth': 20,
    'min_samples_split': 10,
    'min_samples_leaf': 5,
    'max_features': 'sqrt',
    'bootstrap': True,
    'random_state': 42
}
```

### Neural Network (si se implementa)
```python
{
    'architecture': [256, 128, 64, 32],
    'dropout': [0.3, 0.3, 0.2, 0.1],
    'batch_norm': True,
    'activation': 'relu',
    'output_activation': 'softmax',
    'optimizer': 'adam',
    'learning_rate': 0.001,
    'batch_size': 32,
    'epochs': 200,
    'early_stopping_patience': 20
}
```

## 7.3 Criterios para Activar Neural Network

La red neuronal solo se implementa si cumple AL MENOS UNA de estas condiciones:

1. Mejora F1-score >1% sobre XGBoost en validación
2. Mejora Log Loss >0.02 sobre el ensemble base
3. Captura patrones que los modelos tree-based no pueden modelar (interacciones no lineales complejas)

## 7.4 Prevención de Data Leakage

- Split estrictamente **temporal**: entrenar solo con datos anteriores a la fecha de test
- No usar estadísticas futuras (goles del partido actual para predecir el mismo)
- Features calculadas solo con datos disponibles antes del partido
- Validación cruzada con grupos por torneo para evitar fuga entre partidos del mismo torneo

---

# 8. MODELOS DE PREDICCIÓN

## 8.1 Modelo 1: Poisson Bivariante (Goles y Marcadores)

### Propósito
Predecir número de goles de cada equipo y probabilidad de marcadores exactos.

### Fundamento Matemático

La probabilidad de que el equipo local anote `x` goles y el visitante `y` goles es:

```
P(X=x, Y=y) = (e^(-λ₁) × λ₁^x / x!) × (e^(-λ₂) × λ₂^y / y!) × τ
```

Donde:
- `λ₁` = goles esperados del local = exp(β₀ + β₁·AtaqueLocal + β₂·DefensaVisitante + β₃·FactorSede)
- `λ₂` = goles esperados del visitante = exp(γ₀ + γ₁·AtaqueVisitante + γ₂·DefensaLocal)
- `τ` = factor de correlación entre goles (independencia asumida inicialmente)

### Variables para Poisson
- Ataque local (goles promedio últimos 10 partidos como local)
- Defensa local (goles recibidos promedio últimos 10 como local)
- Ataque visitante (goles promedio últimos 10 como visitante)
- Defensa visitante (goles recibidos promedio últimos 10 como visitante)
- Ranking FIFA diferencia
- Ranking Elo diferencia
- Factor sede (mismo país, continente, neutro)
- xG acumulado último N partidos

### Salidas
- Probabilidad de cada marcador (0-0 hasta 10-10)
- Goles esperados por equipo
- Over/Under 0.5, 1.5, 2.5, 3.5, 4.5
- Probabilidad de victoria local, empate, victoria visitante

## 8.2 Modelo 2: XGBoost (Resultado del Partido)

### Propósito
Clasificación multiclase: Victoria Local | Empate | Victoria Visitante

### Arquitectura
- Objective: `multi:softprob`
- NumClass: 3
- Métrica: `mlogloss`

### Variables de Entrada (~150 features)
Todas las variables históricas, de ranking, forma, contexto y avanzadas.

### Salidas
- Probabilidades calibradas para cada resultado
- Feature importance para interpretación

## 8.3 Modelo 3: LightGBM (Estadísticas Avanzadas)

### Propósito
Regresión multi-output para estadísticas detalladas del partido.

### Targets
- Corners local / visitante
- Tiros al arco local / visitante
- Tiros totales local / visitante
- Faltas local / visitante
- Tarjetas amarillas local / visitante
- Tarjetas rojas local / visitante
- Posesión local (%)
- Pases completados local / visitante
- Precisión de pase local / visitante (%)
- Fueras de juego local / visitante
- Recuperaciones local / visitante
- Intercepciones local / visitante

### Arquitectura
- Objective: `regression_l2`
- Multi-output con `MultiOutputRegressor` de scikit-learn
- Métrica: MAE, RMSE, R²

## 8.4 Modelo 4: Random Forest (Benchmark)

### Propósito
Baseline contra el que comparar todos los demás modelos.

### Uso
- Misma configuración que XGBoost
- Evaluar si modelos complejos realmente aportan mejora
- Si RF es competitivo, simplificar el ensemble

## 8.5 Modelo 5: Red Neuronal (Condicional)

### Propósito
Capturar interacciones no lineales complejas que los tree-based no modelan bien.

### Arquitectura Propuesta
```
Input (features)
    ↓
Dense(256) + BatchNorm + Dropout(0.3) + ReLU
    ↓
Dense(128) + BatchNorm + Dropout(0.3) + ReLU
    ↓
Dense(64) + BatchNorm + Dropout(0.2) + ReLU
    ↓
Dense(32) + Dropout(0.1) + ReLU
    ↓
Dense(3) + Softmax (resultado)
    ↓
Dense(2) + Poisson output (goles)
```

### Condición de Activación
Solo se incluye en el ensemble si demuestra mejora estadísticamente significativa.

## 8.6 Ensemble Híbrido

### Estrategia de Combinación

```
Predicción Final = w₁·P_Poisson + w₂·P_XGBoost + w₃·P_LightGBM + w₄·P_RF + w₅·P_NN
```

Donde los pesos `wᵢ` se optimizan en validación mediante:
- **Stacking**: LogisticRegression como meta-learner
- **Weighted Average**: Pesos = 1 / (LogLoss_i) normalizados
- **Bayesian Model Averaging**: Si los modelos son suficientemente diversos

### Calibración
- Platt Scaling para modelos sin calibración intrínseca
- Isotonic Regression si hay suficiente data de validación
- Evaluación con Brier Score y curvas de calibración

---

# 9. VARIABLES Y FEATURE ENGINEERING

## 9.1 Taxonomía de Variables

### Categorías Principales

| Categoría | # Features | Descripción |
|-----------|-----------|-------------|
| Históricas directas | ~30 | Datos crudos de partidos anteriores |
| Derivadas de rendimiento | ~50 | Promedios, eficiencias, ratios |
| Ranking | ~20 | FIFA, Elo, diferencias, tendencias |
| Forma reciente | ~25 | Últimos 5/10/20 partidos, rachas |
| Contextuales | ~15 | Fase, sede, clima, importancia |
| Avanzadas | ~40 | xG, PPDA, presión, posesión territorial |
| Enfrentamiento directo | ~15 | H2H, resultados históricos |
| Plantilla | ~20 | Valor mercado, edad, experiencia |
| Dinámicas | ~30 | Elo time-varying, momentum |
| **Total** | **~245** | |

## 9.2 Variables Detalladas

### Variables Históricas Directas
```
team_games_played_total
team_games_played_home
team_games_played_away
team_games_played_neutral
team_wins_total, team_draws_total, team_losses_total
team_goals_scored_total, team_goals_conceded_total
team_goals_scored_home, team_goals_scored_away
team_goals_conceded_home, team_goals_conceded_away
```

### Variables de Rendimiento (ventanas: 5, 10, 20 partidos)
```
team_avg_goals_scored_last_N
team_avg_goals_conceded_last_N
team_avg_goals_diff_last_N
team_win_rate_last_N
team_draw_rate_last_N
team_loss_rate_last_N
team_points_per_game_last_N
team_avg_corners_for_last_N
team_avg_corners_against_last_N
team_avg_shots_on_target_for_last_N
team_avg_shots_on_target_against_last_N
team_avg_shots_total_for_last_N
team_avg_shots_total_against_last_N
team_avg_fouls_for_last_N
team_avg_fouls_against_last_N
team_avg_yellow_cards_for_last_N
team_avg_red_cards_for_last_N
team_avg_possession_last_N
team_avg_passes_completed_last_N
team_passing_accuracy_last_N
```

### Variables de Ranking
```
fifa_ranking_home, fifa_ranking_away
fifa_ranking_diff (home - away)
fifa_ranking_diff_abs
fifa_ranking_position_home, fifa_ranking_position_away
elo_rating_home, elo_rating_away
elo_rating_diff
elo_rating_diff_abs
fifa_ranking_trend_home (cambio último mes)
elo_rating_trend_away (cambio último mes)
confederation_ranking_home
confederation_ranking_away
```

### Variables de Forma (rachas)
```
team_current_streak (W, D, L consecutivos)
team_unbeaten_streak
team_winning_streak
team_losing_streak
team_goals_scored_streak (partidos seguidos marcando)
team_goals_ conceded_streak (partidos seguidos recibiendo)
team_clean_sheets_last_N
team_failed_to_score_last_N
```

### Variables Contextuales
```
competition_stage (group, round_16, quarter, semi, final)
competition_stage_encoded
match_importance_score (0-100)
is_knockout (bool)
is_group_stage (bool)
is_friendly (bool)
need_to_win (bool: equipo necesita ganar para avanzar)
need_draw (bool: empate suficiente)
pressure_index (combinación de fase + necesidad + contexto)
is_home_team (bool)
is_neutral_venue (bool)
continent_home, continent_away
same_confederation (bool)
temperature_celsius
humidity_percent
altitude_meters
days_since_last_match_home
days_since_last_match_away
travel_distance_home_km
travel_distance_away_km
```

### Variables Avanzadas (xG, Métricas Modernas)
```
team_avg_xG_last_N
team_avg_xGA_last_N (expected goals against)
team_avg_xG_diff_last_N
team_xG_overperformance (goles - xG)
team_xGA_overperformance
team_avg_xA_last_N (expected assists)
team_avg_PPDA_last_N (passes per defensive action)
team_high_press_success_rate
team_territorial_possession_avg_last_N
team_shot_conversion_rate_last_N
team_shots_per_xG_last_N
team_defensive_actions_per_game
team_progressive_passes_per_game
team_progressive_carries_per_game
team_deep_completions_per_game
team_box_entries_per_game
opponent_avg_xG_last_N
opponent_avg_xGA_last_N
opponent_avg_PPDA_last_N
xG_diff_home_away
quality_of_opposition_index (promedio ranking oponentes recientes)
```

### Variables de Elo Dinámico
```
elo_home_current, elo_away_current
elo_home_home_advantage_adjusted
elo_away_away_adjusted
elo_home_recent_form_weighted
elo_away_recent_form_weighted
elo_h2h_history_weighted
elo_momentum_home (tendencia últimos 10 partidos)
elo_momentum_away
elo_volatility_home (desviación estándar últimos 20)
elo_volatility_away
```

### Variables de Plantilla
```
squad_total_value_home, squad_total_value_away
squad_value_diff
squad_avg_age_home, squad_avg_age_away
squad_avg_age_diff
squad_international_experience_avg_caps_home
squad_international_experience_avg_caps_away
squad_players_top5_leagues_home
squad_players_top5_leagues_away
key_player_injuries_home (cantidad)
key_player_injuries_away (cantidad)
key_player_suspensions_home
key_player_suspensions_away
injuries_squad_value_impact_home (valor perdido por lesión)
injuries_squad_value_impact_away
```

### Variables de Enfrentamiento Directo (H2H)
```
h2h_games_played
h2h_home_wins, h2h_draws, h2h_away_wins
h2h_home_goals_avg, h2h_away_goals_avg
h2h_last_meeting_home_goals, h2h_last_meeting_away_goals
h2h_last_meeting_result (home_win, draw, away_win)
h2h_avg_total_goals
h2h_home_win_rate, h2h_away_win_rate
```

### Variables de Interacción (Automáticas)
```
fifa_ranking_diff × is_knockout
avg_goals_scored × opponent_defense_strength
xG_diff × match_importance
home_attack_strength × away_defense_strength
possession_avg × passing_accuracy
```

## 9.3 Feature Pipeline Automatizado

```
┌──────────────────────────────────────────────────────────────┐
│                    FEATURE PIPELINE                           │
│                                                              │
│  Entrada: match_id                                           │
│  ─────────────────────────────────────────────────────       │
│  1. Cargar datos del partido (equipos, fecha, competición)  │
│  2. Calcular ventanas históricas (5/10/20)                  │
│  3. Calcular diferencias entre equipos                     │
│  4. Obtener rankings actuales y tendencias                 │
│  5. Calcular Elo dinámico adaptativo                       │
│  6. Calcular métricas avanzadas (xG, PPDA, etc.)           │
│  7. Calcular features contextuales                         │
│  8. Calcular features H2H                                  │
│  9. Calcular features de plantilla                         │
│  10. Generar interacciones automáticas                     │
│  11. Estandarizar/normalizar según modelo                  │
│  12. Retornar feature vector                               │
│                                                              │
│  Salida: np.array de ~245 features                          │
└──────────────────────────────────────────────────────────────┘
```

## 9.4 Feature Selection

- **Filtrado**: Correlación > 0.95 con otra feature → eliminar una
- **Wrapper**: Recursive Feature Elimination (RFE) con Random Forest
- **Embedded**: Feature importance de XGBoost para mantener top-K
- **SHAP-based**: Seleccionar features con mayor impacto SHAP promedio

---

# 10. ESQUEMA DE BASE DE DATOS

## 10.1 Diagrama Entidad-Relación

```
┌───────────┐     ┌───────────┐     ┌───────────────┐
│  teams    │◄────│  matches  │────►│ competitions  │
└─────┬─────┘     └─────┬─────┘     └───────────────┘
      │                  │
      │            ┌─────┴──────┐       ┌──────────────┐
      │            │            │       │ predictions  │
      │            ▼             ▼       └──────┬───────┘
      │     ┌──────────┐  ┌──────────┐         │
      │     │team_stats│  │player_stats│        │
      │     └──────────┘  └────────────┘        │
      │                                         │
      │     ┌──────────┐       ┌────────────┐   │
      ├────►│ players  │──────►│ injuries   │   │
      │     └──────────┘       └────────────┘   │
      │                                         │
      │     ┌──────────┐       ┌────────────┐   │
      └────►│rankings  │       │suspensions │   │
            └──────────┘       └────────────┘   │
                                                │
┌──────────────┐       ┌──────────────────┐     │
│scraping_logs │       │model_versions    │─────┘
└──────────────┘       └──────────────────┘
```

## 10.2 Esquema Detallado

### teams
```sql
CREATE TABLE teams (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    full_name       VARCHAR(200),
    code            VARCHAR(3),             -- FIFA 3-letter code
    country         VARCHAR(100),
    confederation   VARCHAR(50),             -- UEFA, CONMEBOL, etc.
    founded_year    INTEGER,
    logo_url        VARCHAR(500),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(name)
);

CREATE INDEX idx_teams_confederation ON teams(confederation);
CREATE INDEX idx_teams_name ON teams(name);
```

### competitions
```sql
CREATE TABLE competitions (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    short_name      VARCHAR(50),
    type            VARCHAR(50),             -- world_cup, continental_cup, league, friendly
    confederation   VARCHAR(50),
    season          VARCHAR(20),
    start_date      DATE,
    end_date        DATE,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(name, season)
);

CREATE INDEX idx_competitions_type ON competitions(type);
```

### matches
```sql
CREATE TABLE matches (
    id              SERIAL PRIMARY KEY,
    competition_id  INTEGER REFERENCES competitions(id),
    season          VARCHAR(20),
    stage           VARCHAR(50),             -- group, round_of_16, quarter_final, semi_final, final
    round           INTEGER,
    group_name      VARCHAR(10),
    match_date      DATE NOT NULL,
    match_time      TIME,
    home_team_id    INTEGER REFERENCES teams(id) NOT NULL,
    away_team_id    INTEGER REFERENCES teams(id) NOT NULL,
    home_score      INTEGER,
    away_score      INTEGER,
    home_goals_ht   INTEGER,                 -- half time
    away_goals_ht   INTEGER,
    home_xg         DECIMAL(5,2),
    away_xg         DECIMAL(5,2),
    venue           VARCHAR(200),
    city            VARCHAR(100),
    country         VARCHAR(100),
    stadium         VARCHAR(200),
    attendance      INTEGER,
    temperature     DECIMAL(5,1),
    humidity        INTEGER,
    altitude        INTEGER,
    weather_condition VARCHAR(100),
    referee         VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(competition_id, home_team_id, away_team_id, match_date)
);

CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_home ON matches(home_team_id);
CREATE INDEX idx_matches_away ON matches(away_team_id);
CREATE INDEX idx_matches_competition ON matches(competition_id);
CREATE INDEX idx_matches_stage ON matches(stage);
```

### players
```sql
CREATE TABLE players (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    full_name       VARCHAR(300),
    team_id         INTEGER REFERENCES teams(id),
    position        VARCHAR(30),             -- GK, DEF, MID, FWD
    position_detail VARCHAR(50),             -- CB, LB, CDM, CAM, LW, ST...
    date_of_birth   DATE,
    age             INTEGER,
    nationality     VARCHAR(100),
    height_cm       INTEGER,
    weight_kg       INTEGER,
    foot            VARCHAR(10),             -- left, right, both
    market_value_eur DECIMAL(12,2),
    current_club    VARCHAR(200),
    shirt_number    INTEGER,
    international_caps INTEGER,
    international_goals INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_players_team ON players(team_id);
CREATE INDEX idx_players_position ON players(position);
```

### rankings
```sql
CREATE TABLE rankings (
    id              SERIAL PRIMARY KEY,
    team_id         INTEGER REFERENCES teams(id) NOT NULL,
    ranking_type    VARCHAR(20) NOT NULL,     -- fifa, elo
    rank            INTEGER NOT NULL,
    previous_rank   INTEGER,
    points          DECIMAL(8,2),
    change_points   DECIMAL(8,2),
    rank_date       DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, ranking_type, rank_date)
);

CREATE INDEX idx_rankings_team_date ON rankings(team_id, rank_date);
CREATE INDEX idx_rankings_type_date ON rankings(ranking_type, rank_date DESC);
CREATE INDEX idx_rankings_date ON rankings(rank_date);
```

### team_stats
```sql
CREATE TABLE team_stats (
    id                      SERIAL PRIMARY KEY,
    match_id                INTEGER REFERENCES matches(id) NOT NULL,
    team_id                 INTEGER REFERENCES teams(id) NOT NULL,
    is_home                 BOOLEAN NOT NULL,
    goals                   INTEGER,
    xg                      DECIMAL(5,2),
    xga                     DECIMAL(5,2),     -- expected goals against
    shots_total             INTEGER,
    shots_on_target         INTEGER,
    shots_off_target        INTEGER,
    shots_blocked           INTEGER,
    corners                 INTEGER,
    fouls                   INTEGER,
    yellow_cards            INTEGER,
    red_cards               INTEGER,
    possession              DECIMAL(5,1),     -- percentage
    passes_total            INTEGER,
    passes_completed        INTEGER,
    passing_accuracy        DECIMAL(5,1),
    progressive_passes      INTEGER,
    progressive_carries     INTEGER,
    deep_completions        INTEGER,
    box_entries             INTEGER,
    crosses                 INTEGER,
    crosses_accuracy        DECIMAL(5,1),
    offsides                INTEGER,
    tackles                 INTEGER,
    interceptions           INTEGER,
    clearances              INTEGER,
    blocks                  INTEGER,
    recoveries              INTEGER,
    saves                   INTEGER,          -- if GK
    ppda                    DECIMAL(6,2),     -- passes per defensive action
    high_press_success      INTEGER,
    territorial_possession  DECIMAL(5,1),     -- % in opponent half
    shot_conversion_rate    DECIMAL(5,2),
    avg_shot_distance       DECIMAL(4,1),
    expected_goals_on_target DECIMAL(5,2),
    created_at              TIMESTAMP DEFAULT NOW(),
    UNIQUE(match_id, team_id)
);

CREATE INDEX idx_team_stats_match ON team_stats(match_id);
CREATE INDEX idx_team_stats_team ON team_stats(team_id);
```

### player_stats
```sql
CREATE TABLE player_stats (
    id                      SERIAL PRIMARY KEY,
    match_id                INTEGER REFERENCES matches(id) NOT NULL,
    player_id               INTEGER REFERENCES players(id) NOT NULL,
    team_id                 INTEGER REFERENCES teams(id) NOT NULL,
    minutes_played          INTEGER,
    position                VARCHAR(30),
    rating                  DECIMAL(4,2),
    goals                   INTEGER DEFAULT 0,
    assists                 INTEGER DEFAULT 0,
    xg                      DECIMAL(5,2),
    xa                      DECIMAL(5,2),
    shots_total             INTEGER DEFAULT 0,
    shots_on_target         INTEGER DEFAULT 0,
    goals_per_shot          DECIMAL(5,3),
    key_passes              INTEGER DEFAULT 0,
    passes_total            INTEGER DEFAULT 0,
    passes_completed        INTEGER DEFAULT 0,
    passing_accuracy        DECIMAL(5,1),
    progressive_passes      INTEGER DEFAULT 0,
    assists_per_90          DECIMAL(5,2),
    goals_per_90            DECIMAL(5,2),
    dribbles_successful     INTEGER DEFAULT 0,
    dribbles_attempted      INTEGER DEFAULT 0,
    tackles                 INTEGER DEFAULT 0,
    interceptions           INTEGER DEFAULT 0,
    clearances              INTEGER DEFAULT 0,
    blocks                  INTEGER DEFAULT 0,
    fouls                   INTEGER DEFAULT 0,
    fouls_suffered          INTEGER DEFAULT 0,
    yellow_cards            INTEGER DEFAULT 0,
    red_cards               INTEGER DEFAULT 0,
    offsides                INTEGER DEFAULT 0,
    recoveries              INTEGER DEFAULT 0,
    aerials_won             INTEGER DEFAULT 0,
    aerials_total           INTEGER DEFAULT 0,
    created_at              TIMESTAMP DEFAULT NOW(),
    UNIQUE(match_id, player_id)
);

CREATE INDEX idx_player_stats_match ON player_stats(match_id);
CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_team ON player_stats(team_id);
```

### injuries
```sql
CREATE TABLE injuries (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER REFERENCES players(id) NOT NULL,
    team_id         INTEGER REFERENCES teams(id) NOT NULL,
    injury_type     VARCHAR(100),
    injury_area     VARCHAR(100),
    severity        VARCHAR(50),             -- minor, moderate, severe, critical
    expected_return DATE,
    start_date      DATE NOT NULL,
    end_date        DATE,
    status          VARCHAR(20) DEFAULT 'active', -- active, recovered
    importance      VARCHAR(20),             -- key_player, regular, squad
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_injuries_player ON injuries(player_id);
CREATE INDEX idx_injuries_team_status ON injuries(team_id, status);
CREATE INDEX idx_injuries_date ON injuries(start_date);
```

### suspensions
```sql
CREATE TABLE suspensions (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER REFERENCES players(id) NOT NULL,
    team_id         INTEGER REFERENCES teams(id) NOT NULL,
    match_id        INTEGER REFERENCES matches(id),
    reason          VARCHAR(200),            -- yellow_card_accumulation, red_card, disciplinary
    start_date      DATE NOT NULL,
    end_date        DATE,
    matches_missed  INTEGER,
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_suspensions_player ON suspensions(player_id);
CREATE INDEX idx_suspensions_team ON suspensions(team_id);
```

### predictions
```sql
CREATE TABLE predictions (
    id                      SERIAL PRIMARY KEY,
    match_id                INTEGER REFERENCES matches(id) NOT NULL,
    model_version_id        INTEGER REFERENCES model_versions(id),
    prediction_date         TIMESTAMP DEFAULT NOW(),
    
    -- Resultado
    home_win_probability     DECIMAL(6,4),
    draw_probability         DECIMAL(6,4),
    away_win_probability     DECIMAL(6,4),
    predicted_result         VARCHAR(10),     -- H, D, A
    
    -- Goles
    home_goals_expected      DECIMAL(5,2),
    away_goals_expected      DECIMAL(5,2),
    total_goals_expected     DECIMAL(5,2),
    over_05_probability      DECIMAL(6,4),
    over_15_probability      DECIMAL(6,4),
    over_25_probability      DECIMAL(6,4),
    over_35_probability      DECIMAL(6,4),
    over_45_probability      DECIMAL(6,4),
    btts_probability         DECIMAL(6,4),   -- both teams to score
    
    -- Marcador exacto (JSON)
    exact_score_probabilities JSONB,
    most_likely_score        VARCHAR(10),
    most_likely_score_prob   DECIMAL(6,4),
    
    -- Estadísticas avanzadas
    predicted_home_corners    DECIMAL(5,2),
    predicted_away_corners    DECIMAL(5,2),
    predicted_home_shots_ot   DECIMAL(5,2),
    predicted_away_shots_ot   DECIMAL(5,2),
    predicted_home_shots      DECIMAL(5,2),
    predicted_away_shots      DECIMAL(5,2),
    predicted_home_fouls      DECIMAL(5,2),
    predicted_away_fouls      DECIMAL(5,2),
    predicted_home_yellow     DECIMAL(5,2),
    predicted_away_yellow     DECIMAL(5,2),
    predicted_home_red        DECIMAL(5,2),
    predicted_away_red        DECIMAL(5,2),
    predicted_home_possession DECIMAL(5,2),
    predicted_away_possession DECIMAL(5,2),
    predicted_home_offsides   DECIMAL(5,2),
    predicted_away_offsides   DECIMAL(5,2),
    predicted_home_passes_completed DECIMAL(6,1),
    predicted_away_passes_completed DECIMAL(6,1),
    predicted_home_passing_accuracy  DECIMAL(5,2),
    predicted_away_passing_accuracy  DECIMAL(5,2),
    predicted_home_recoveries DECIMAL(5,2),
    predicted_away_recoveries DECIMAL(5,2),
    predicted_home_interceptions DECIMAL(5,2),
    predicted_away_interceptions DECIMAL(5,2),
    
    -- Métricas de confianza
    confidence_score         DECIMAL(5,2),   -- 0-100
    model_agreement          DECIMAL(5,2),   -- qué % de modelos coinciden
    prediction_std           DECIMAL(6,4),   -- desviación entre modelos
    
    -- SHAP explicación (JSON)
    shap_values              JSONB,
    top_features             JSONB,
    
    created_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_predictions_match ON predictions(match_id);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_predictions_model ON predictions(model_version_id);
```

### model_versions
```sql
CREATE TABLE model_versions (
    id              SERIAL PRIMARY KEY,
    model_name      VARCHAR(50) NOT NULL,     -- poisson, xgboost, lightgbm, rf, nn, ensemble
    version         VARCHAR(20) NOT NULL,      -- semantic version
    model_type      VARCHAR(50),              -- classification, regression, poisson
    parameters      JSONB,                    -- hyperparameters used
    metrics         JSONB,                    -- performance metrics
    training_date   TIMESTAMP DEFAULT NOW(),
    training_data_range_start DATE,
    training_data_range_end DATE,
    data_hash       VARCHAR(64),              -- hash of training data for reproducibility
    model_file_path VARCHAR(300),             -- path to serialized model
    feature_list    JSONB,                    -- list of features used
    feature_count   INTEGER,
    status          VARCHAR(20) DEFAULT 'active', -- active, deprecated, archived
    is_ensemble     BOOLEAN DEFAULT FALSE,
    parent_models   JSONB,                    -- if ensemble, list of model_version_ids
    accuracy        DECIMAL(6,4),
    precision       DECIMAL(6,4),
    recall          DECIMAL(6,4),
    f1_score        DECIMAL(6,4),
    roc_auc         DECIMAL(6,4),
    log_loss        DECIMAL(6,4),
    brier_score     DECIMAL(6,4),
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### scraping_logs
```sql
CREATE TABLE scraping_logs (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(100) NOT NULL,
    url             VARCHAR(500),
    data_type       VARCHAR(50),             -- ranking, match, player, stats
    status          VARCHAR(20) NOT NULL,     -- success, failed, partial
    items_count     INTEGER,
    error_message   TEXT,
    started_at      TIMESTAMP,
    finished_at     TIMESTAMP,
    duration_ms     INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scraping_logs_status ON scraping_logs(status);
CREATE INDEX idx_scraping_logs_source ON scraping_logs(source);
CREATE INDEX idx_scraping_logs_date ON scraping_logs(created_at);
```

---

# 11. MÉTRICAS AVANZADAS

## 11.1 Expected Goals (xG)

### Qué es
Métrica que cuantifica la probabilidad de que un disparo se convierta en gol, basada en las características del disparo.

### Factores que componen xG
- Distancia al arco
- Ángulo del disparo
- Tipo de asistencia (pase filtrado, centro, rebote)
- Parte del cuerpo (pierna derecha, izquierda, cabeza)
- Situación de juego (jugada, tiro libre, penal, córner)
- Presión defensiva
- Posición de los defensores
- Posición del arquero

### Implementación
Dado que no tenemos acceso a datos de tracking de disparos para partidos históricos, implementaremos:

1. **xG Modelo Base**: Regresión logística entrenada con datos públicos de más de 100,000 disparos
2. **Calibración**: Ajuste por torneo/liga usando datos agregados
3. **Actualización**: Cuando tengamos datos de tracking, refinar el modelo

```python
# Pseudo-código del modelo xG
xG = 1 / (1 + exp(-(β₀ + β₁·distancia + β₂·ángulo + β₃·cabeza + β₄·asistencia + β₅·presión)))
```

## 11.2 Expected Assists (xA)

Métrica que valora la probabilidad de que un pase se convierta en asistencia de gol.

### Factores
- Tipo de pase (filtrado, centro, pase largo, pase corto)
- Zona de origen del pase
- Zona de destino del pase
- Presión al pasador
- Tipo de ataque (rápido, posicional, contraataque)

## 11.3 PPDA (Passes Per Defensive Action)

### Definición
Número de pases que permite un equipo antes de realizar una acción defensiva (tackle, intercepción, falta, despeje).

### Interpretación
- **PPDA bajo (< 10)**: Presión alta intensa
- **PPDA medio (10-15)**: Presión moderada
- **PPDA alto (> 15)**: Presión baja, bloque bajo

### Implementación
```python
PPDA = passes_opponent / (tackles + interceptions + fouls + clearances)
```

### Valor Predictivo
Equipos con PPDA consistentemente bajo tienden a:
- Recuperar el balón más rápido
- Generar más oportunidades en campo rival
- Someterse a menos ataques organizados

## 11.4 Posesión Territorial

No es solo posesión del balón, sino posesión en zonas peligrosas.

### Componentes
- **Posesión total**: % de tiempo con el balón
- **Posesión en campo rival**: % en mitad rival
- **Posesión en último tercio**: % en zona de ataque
- **Posesión en área**: % en área rival

### Valor Predictivo
La posesión en último tercio correlaciona mejor con goles que la posesión total.

## 11.5 Presión Alta (High Press)

### Métricas
- **Acciones de presión por minuto**: Intensidad defensiva
- **% de presiones exitosas**: Presiones que resultan en recuperación
- **Recuperaciones en campo rival**: Balones recuperados en zona ofensiva

## 11.6 Shot Conversion Rate

```python
conversion_rate = goals / shots_on_target
```

### Valor Predictivo
Equipos con alta tasa de conversión sostenida suelen tener delanteros de calidad. Equipos con tasa anormalmente alta (>25%) probablemente regresarán a la media.

## 11.7 Ratings Elo Dinámicos

### Implementación de Elo Mejorado

Elo base con modificaciones específicas para fútbol:

```python
def calculate_elo(team_a_rating, team_b_rating, result, margin, home_advantage=True):
    """
    result: 1 = win, 0.5 = draw, 0 = loss
    margin: goal difference
    """
    K_base = 32  # K-factor base
    K_knockout = 48  # K-factor para eliminatorias
    K_friendly = 20  # K-factor para amistosos
    
    expected = 1 / (1 + 10^((team_b_rating - team_a_rating) / 400))
    
    # Ajuste por margen de goles (goleadas pesan más)
    margin_multiplier = ln(margin + 1)
    if margin > 2:
        margin_multiplier *= 1.5
    
    # Ajuste si el resultado fue inesperado
    upset_multiplier = abs(result - expected) * 2
    
    K = K_base
    if competition == 'world_cup_knockout':
        K = K_knockout
    elif competition == 'friendly':
        K = K_friendly
    
    new_rating = team_a_rating + K * margin_multiplier * upset_multiplier * (result - expected)
    
    return new_rating
```

### Ajustes Adicionales
- **Ventaja local**: +50-70 puntos Elo por localía
- **Altitud**: +20-30 puntos Elo para equipos locales en altura
- **Fatiga**: -5 puntos Elo por cada día de descanso < 4

---

# 12. API Y SERVICIOS

## 12.1 Endpoints REST

### Predicción
```
GET  /api/v1/predictions/{match_id}         → Predicción completa de un partido
POST /api/v1/predictions                    → Generar nueva predicción
GET  /api/v1/predictions/upcoming           → Predicciones para próximos partidos
GET  /api/v1/predictions/history            → Historial de predicciones pasadas
GET  /api/v1/predictions/{match_id}/explain → Explicación SHAP de la predicción
```

### Partidos
```
GET    /api/v1/matches                      → Listar partidos (filtros: fecha, torneo, equipo)
GET    /api/v1/matches/{match_id}           → Detalle del partido
GET    /api/v1/matches/{match_id}/stats     → Estadísticas del partido
```

### Equipos
```
GET /api/v1/teams                           → Listar equipos
GET /api/v1/teams/{team_id}                 → Detalle del equipo
GET /api/v1/teams/{team_id}/history         → Historial de partidos
GET /api/v1/teams/{team_id}/stats           → Estadísticas agregadas
```

### Rankings
```
GET /api/v1/rankings/fifa                   → Ranking FIFA actual
GET /api/v1/rankings/elo                    → Ranking Elo actual
GET /api/v1/rankings/{team_id}/history      → Historial de ranking
```

### Modelos
```
GET /api/v1/models                          → Listar modelos disponibles
GET /api/v1/models/{model_id}               → Detalle del modelo
GET /api/v1/models/metrics                  → Comparativa de métricas
POST /api/v1/models/train                   → Iniciar entrenamiento
```

### Jugadores
```
GET /api/v1/players                         → Listar jugadores
GET /api/v1/players/{player_id}             → Detalle del jugador
GET /api/v1/players/{player_id}/stats       → Estadísticas del jugador
```

### Scraping (Admin)
```
POST   /api/v1/admin/scrape/rankings        → Forzar scraping rankings
POST   /api/v1/admin/scrape/matches         → Forzar scraping partidos
POST   /api/v1/admin/scrape/players         → Forzar scraping jugadores
GET    /api/v1/admin/scrape/status          → Estado de scraping
GET    /api/v1/admin/scrape/logs            → Logs de scraping
```

## 12.2 Estructura de Servicios

### prediction_service.py (Orquestador Principal)
```python
class PredictionService:
    def __init__(self):
        self.feature_service = FeatureService()
        self.model_loader = ModelLoader()
        self.explainability_service = ExplainabilityService()
    
    def predict(self, match_id: int) -> PredictionResult:
        # 1. Generar features
        features = self.feature_service.generate_features(match_id)
        
        # 2. Cargar modelos activos
        models = self.model_loader.load_active_models()
        
        # 3. Predecir con cada modelo
        predictions = []
        for model in models:
            pred = model.predict(features)
            predictions.append(pred)
        
        # 4. Ensemble
        ensemble_result = self._ensemble(predictions)
        
        # 5. Explicabilidad
        explanation = self.explainability_service.explain(
            models, features, ensemble_result
        )
        
        # 6. Persistir
        self._save_prediction(match_id, ensemble_result, explanation)
        
        return PredictionResult(
            probabilities=ensemble_result.probabilities,
            scores=ensemble_result.scores,
            advanced_stats=ensemble_result.advanced_stats,
            explanation=explanation
        )
```

---

# 13. FRONTEND Y DASHBOARD

## 13.1 Estructura del Dashboard

### Páginas Principales

| Página | Descripción | Componentes Clave |
|--------|-------------|-------------------|
| **Home** | Predicciones próximos partidos | Tarjetas de partido, barras de probabilidad, timeline |
| **Match Detail** | Predicción detallada de un partido | Probabilidades, marcadores, stats, SHAP force plot |
| **Compare** | Comparativa entre dos equipos | Radar chart, stats cabeza a cabeza |
| **Standings** | Rankings FIFA/Elo + tendencias | Tablas interactivas, sparklines |
| **History** | Historial de predicciones vs reales | Scatter plot, accuracy timeline |
| **Models** | Rendimiento de modelos | Métricas, comparativas, confusión matrix |
| **Admin** | Gestión de scraping y ETL | Logs, triggers, estado del sistema |

## 13.2 Layout del Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]  Predicción Deportiva    [Partidos] [Equipos] [Admin]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PARTIDOS PRÓXIMOS (PRÓXIMOS 7 DÍAS)                       │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │ │
│  │  │ Brasil   │  │ España   │  │ Francia  │  │ Argentina│   │ │
│  │  │ vs       │  │ vs       │  │ vs       │  │ vs       │   │ │
│  │  │ Alemania │  │ Italia   │  │ Inglaterra│ │ Portugal │   │ │
│  │  │ [65/20/15]│  │ [55/25/20]│  │ [60/22/18]│  │ [58/23/19]│ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┐        │
│  │ Análisis│ Gráfico  │ Marcador │ Over/    │ Stats    │        │
│  │ Result.│ Probab.  │ Exacto   │ Under    │ Avanzadas│        │
│  ├─────────┼──────────┼──────────┼──────────┼──────────┤        │
│  │ H: 65%  │ [Donut]  │ 2-1: 12% │ O2.5:68% │ Corners  │        │
│  │ D: 20%  │ [Bar]    │ 1-0: 10% │ U2.5:32% │ Tiros    │        │
│  │ A: 15%  │ [Radar]  │ 2-0: 9%  │ O3.5:45% │ Posesión │        │
│  └─────────┴──────────┴──────────┴──────────┴──────────┘        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  EXPLICACIÓN DE LA PREDICCIÓN                               │ │
│  │                                                             │ │
│  │  • Ranking FIFA: Brasil (3º) vs Alemania (10º) → +12%      │ │
│  │  • Forma reciente: Brasil ganó 4/5 → +8%                   │ │
│  │  • Historial H2H: Brasil dominante → +5%                   │ │
│  │  • Fase: Grupos (presión media) → +2%                      │ │
│  │  • SHAP Force Plot: [visualización interactiva]             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  COMPARATIVA BRASIL VS ALEMANIA                            │ │
│  │  [Radar Chart con stats lado a lado]                       │ │
│  │                                                             │ │
│  │  Ataque:      9.2 vs 8.1                                   │ │
│  │  Defensa:     8.8 vs 7.5                                   │ │
│  │  Posesión:    62% vs 55%                                   │ │
│  │  xG/partido:  2.1 vs 1.8                                   │ │
│  │  PPDA:        9.5 vs 11.2                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  Footer: © 2025 Predicción Deportiva. Datos actualizados: ...  │
└─────────────────────────────────────────────────────────────────┘
```

## 13.3 Componentes Clave del Frontend

### 1. Tarjeta de Predicción de Partido
```html
<div class="match-card">
    <div class="match-header">
        <span class="competition-badge">World Cup 2026</span>
        <span class="stage-badge">Semifinal</span>
    </div>
    <div class="match-teams">
        <div class="team home">
            <img src="flag.png" alt="Brasil">
            <span class="team-name">Brasil</span>
            <span class="team-rank">#3 FIFA</span>
        </div>
        <div class="match-probability-bar">
            <div class="bar home" style="width: 65%">65%</div>
            <div class="bar draw" style="width: 20%">20%</div>
            <div class="bar away" style="width: 15%">15%</div>
        </div>
        <div class="team away">
            <img src="flag.png" alt="Alemania">
            <span class="team-name">Alemania</span>
            <span class="team-rank">#10 FIFA</span>
        </div>
    </div>
    <div class="match-stats-preview">
        <div class="stat"><span>xG</span><strong>2.1 - 1.4</strong></div>
        <div class="stat"><span>Score</span><strong>2-1 (12%)</strong></div>
        <div class="stat"><span>O2.5</span><strong>68%</strong></div>
    </div>
</div>
```

### 2. SHAP Force Plot (JavaScript)
```javascript
// Usando SHAP.js o implementación personalizada con Chart.js
// Cada feature contribuye positiva o negativamente
const shapData = {
    features: [
        { name: 'Ranking FIFA Diff', value: +7, contribution: +0.12 },
        { name: 'Forma Reciente', value: '4/5 wins', contribution: +0.08 },
        { name: 'H2H Historial', value: 'Dominante', contribution: +0.05 },
        { name: 'Lesiones Clave', value: '2 bajas', contribution: -0.03 },
        // ...
    ]
};
```

### 3. Radar de Comparativa (Chart.js)
```javascript
new Chart(ctx, {
    type: 'radar',
    data: {
        labels: ['Ataque', 'Defensa', 'Posesión', 'xG', 'PPDA', 'Forma'],
        datasets: [{
            label: 'Brasil',
            data: [92, 88, 85, 90, 78, 95],
            borderColor: '#ffd700'
        }, {
            label: 'Alemania',
            data: [81, 75, 72, 80, 82, 70],
            borderColor: '#000000'
        }]
    }
});
```

---

# 14. DEVOPS E INFRAESTRUCTURA

## 14.1 Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: prediccion_deportiva
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: ${FLASK_ENV}
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/prediccion_deportiva
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./data:/app/data
    command: gunicorn -w 4 -b 0.0.0.0:5000 src.api.app:app

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/prediccion_deportiva
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./data:/app/data
    command: celery -A src.infrastructure.celery_worker worker --loglevel=info

  scheduler:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/prediccion_deportiva
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    command: python -m src.etl.scheduler

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./infra/nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./src/static:/app/static
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

## 14.2 Variables de Entorno (.env)

```bash
# Database
DB_USER=prediccion_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=prediccion_deportiva

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Scraping
SCRAPER_USER_AGENT_ROTATE=True
SCRAPER_DELAY_MIN=1.0
SCRAPER_DELAY_MAX=3.0
SCRAPER_PROXY_ENABLED=False

# ML
ML_MODELS_DIR=./data/models
ML_FEATURES_CACHE_DIR=./data/cache
ML_RANDOM_SEED=42

# Logging
LOG_LEVEL=INFO
LOG_FILE=./data/logs/app.log
```

## 14.3 CI/CD Pipeline

```yaml
# .github/workflows/main.yml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Lint
        run: flake8 src/ tests/
      - name: Type check
        run: mypy src/
      - name: Run tests
        run: pytest tests/ -v --cov=src --cov-report=term
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_db

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t prediccion-deportiva:${{ github.sha }} .
      - name: Tag and push
        run: |
          docker tag prediccion-deportiva:${{ github.sha }} \
            registry.example.com/prediccion-deportiva:latest
          # docker push ...
```

## 14.4 Logging

### Formato de Logs
```python
{
    "timestamp": "2025-01-15T14:30:00.123Z",
    "level": "INFO",
    "service": "prediction_service",
    "module": "predict_match",
    "action": "generate_prediction",
    "match_id": 1234,
    "duration_ms": 345,
    "models_used": ["poisson", "xgboost", "lightgbm"],
    "status": "success"
}
```

### Niveles de Log
- **ERROR**: Fallos en predicción, scraping, DB
- **WARNING**: Tasa de error alta, datos incompletos, modelo degradado
- **INFO**: Predicciones generadas, scraping completado, ETL ejecutado
- **DEBUG**: Features generadas, tiempos de inferencia, datos crudos

---

# 15. JUSTIFICACIÓN TÉCNICA

## 15.1 Decisiones Arquitectónicas

### ¿Por qué Flask y no FastAPI?

| Aspecto | Flask | FastAPI |
|---------|-------|---------|
| Templates | Jinja2 nativo | Jinja2 pero no es el foco |
| Ecosistema | Más maduro para dashboards server-side | Excelente para APIs puras |
| Rendimiento | Suficiente (Gunicorn + workers) | Superior (ASGI) |
| Complejidad | Menor para full-stack | Mayor si añades frontend |

**Decisión**: Flask porque el frontend es server-side rendering. Si en el futuro separamos frontend (SPA), migrar la API a FastAPI es trivial.

### ¿Por qué PostgreSQL y no MongoDB?

- Los datos de fútbol son altamente relacionales (equipos → partidos → estadísticas)
- Necesitamos joins complejos para feature engineering
- PostgreSQL con JSONB ofrece flexibilidad documental para datos semiestructurados (SHAP values, configuraciones de modelo)
- Las consultas analíticas (ventanas, agregaciones) son órdenes de magnitud más rápidas en PostgreSQL

### ¿Por qué Scrapy y no BeautifulSoup para todo?

Scrapy proporciona:
- Framework completo con middleware (proxies, user-agents, caching)
- Pipeline de datos integrado (transformación → DB)
- Manejo de concurrencia y rate limiting nativo
- Respeto de robots.txt automático

BeautifulSoup se usa solo para tareas específicas (parsear HTML de una página concreta sin navegación compleja).

### ¿Por qué APScheduler y no Airflow?

Airflow es la herramienta correcta para pipelines complejos con dependencias entre DAGs, pero para este proyecto:
- Solo hay ~15 tareas ETL con dependencias lineales
- La sobrecarga operativa de Airflow (base de datos, webserver, scheduler, workers) no se justifica
- APScheduler + Celery ofrece el 90% de la funcionalidad con 10% de la complejidad

### ¿Por qué modelos separados y no un solo modelo gigante?

1. **Rendimiento**: Modelos especializados superan a modelos generalistas
2. **Mantenibilidad**: Cada modelo se puede mejorar/actualizar independientemente
3. **Interpretabilidad**: Más fácil entender por qué cada modelo contribuye de cierta manera
4. **Robustez**: Si un modelo falla, los demás siguen funcionando
5. **Experimentación**: Permite probar nuevas arquitecturas sin afectar el sistema

### ¿Por qué Poisson + Tree-based + Ensemble?

- **Poisson**: Modelo estadístico con fundamento teórico probado para goles en fútbol. No necesita grandes volúmenes de datos.
- **XGBoost/LightGBM**: Capturan interacciones complejas y patrones no lineales que Poisson no puede modelar.
- **Ensemble**: Combina las fortalezas de ambos. Poisson captura la estructura base de goles, Tree-based modela el contexto y las interacciones.

### ¿Por qué no usar un modelo pre-entrenado (API externa)?

1. Costo: Las APIs de predicción deportiva son caras y tienen límites de uso
2. Control: Necesitamos control total sobre las features y el entrenamiento
3. Personalización: El modelo debe adaptarse a torneos específicos
4. Explicabilidad: Las APIs externas son cajas negras
5. Independencia: El sistema debe funcionar sin dependencia de terceros

## 15.2 Decisiones de ML

### Balanceo de Clases

El fútbol tiene un desbalance natural: más victorias locales que visitantes (≈45% H, 28% D, 27% A).

Estrategias:
- **Weighted classes**: Pesos inversamente proporcionales a frecuencia
- **SMOTE**: Solo si el desbalance es muy extremo (no es el caso)
- **Stratified CV**: Mantener distribución en cada fold

### Manejo de Datos Faltantes

- **Rankings**: Si no hay FIFA, usar Elo. Si no hay Elo, imputar con promedio del continente
- **Estadísticas avanzadas (xG, PPDA)**: Imputar con medianas históricas del torneo
- **Clima**: Usar promedio histórico de la sede en esa fecha
- **Lesiones**: Si no hay datos, asumir plantilla completa

### Estrategia de Validación Temporal

No usar random split. El split debe ser temporal:
- Train: Partidos hasta 2018
- Validation: Partidos 2019-2022
- Test: Partidos 2023 en adelante

Para la Copa del Mundo:
- Train: Copas 1930-2014
- Validation: Copa 2018
- Test: Copa 2022

### Métrica Principal de Optimización

**Log Loss** (Cross-Entropy) para clasificación:
- Penaliza predicciones seguras pero incorrectas más que predicciones inseguras
- Es la métrica estándar para clasificación probabilística
- Se alinea con el objetivo de tener probabilidades bien calibradas

---

# 16. RIESGOS Y LIMITACIONES

## 16.1 Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Datos insuficientes para equipos pequeños | Alta | Medio | Transfer learning, priors Bayesianos |
| Cambios en APIs externas | Media | Alto | Scraping como fallback, monitoreo continuo |
| Sobreajuste a datos históricos | Media | Alto | Validación temporal estricta, early stopping |
| Lesiones de última hora no capturadas | Alta | Medio | Actualización diaria, permitir ajuste manual |
| Partidos impredecibles (clásicos, derbis) | Alta | Bajo | El modelo debe reflejar incertidumbre |
| Desbalance de clases | Baja | Medio | Weighted training, stratified CV |
| Data leakage por features futuras | Media | Alto | Pipeline de features con validación temporal |
| Costo computacional del reentrenamiento | Baja | Medio | Entrenamiento incremental, modelos ligeros |

## 16.2 Limitaciones Conocidas

1. **xG sin datos de tracking**: Nuestro modelo xG será menos preciso que el de proveedores con datos de tracking (Opta, StatsBomb).
2. **Factor humano**: No podemos modelar motivación, conflictos internos, problemas personales de jugadores.
3. **Eventos raros**: Tarjetas rojas, penales, autogoles tienen baja frecuencia y son difíciles de predecir.
4. **Cambios de reglas**: Modificaciones en el reglamento (VAR, número de cambios) afectan patrones históricos.
5. **Datos de lesiones**: La calidad de datos de lesiones varía enormemente entre torneos.
6. **Estacionalidad**: El rendimiento en mundiales difiere del rendimiento en ligas (diferente contexto, presión, preparación).
7. **Efecto sorpresa**: Equipos que emergen sin historial suficiente (ej: Croacia 2018, Marruecos 2022).

## 16.3 Principios Éticos

1. **Transparencia**: Toda predicción incluye fundamentos y nivel de confianza
2. **No apuestas**: El sistema no está diseñado ni debe usarse para apuestas
3. **Privacidad de datos**: Solo se usan datos públicos
4. **Responsabilidad**: Las predicciones son probabilísticas, no deterministas

---

# 17. MEJORAS FUTURAS

## 17.1 Corto Plazo (3-6 meses)

- [ ] **Datos en tiempo real**: Integrar APIs de tiempo real para predicciones durante el partido (live betting odds)
- [ ] **Modelo de lesiones**: ML para predecir probabilidad de lesión basado en carga de minutos
- [ ] **Sistema de alertas**: Notificaciones cuando cambien significativamente las probabilidades
- [ ] **API pública**: Endpoints documentados para integración externa
- [ ] **Datos de tracking**: Integrar Opta/StatsBomb cuando haya presupuesto

## 17.2 Mediano Plazo (6-12 meses)

- [ ] **Predicción de mercado de pases**: Impacto de nuevos fichajes en rendimiento
- [ ] **Análisis de estilo de juego**: Clustering de equipos por estilo (tiki-taka, contraataque, presión alta)
- [ ] **Modelo de formaciones**: Impacto de la formación táctica en el resultado
- [ ] **Simulación Monte Carlo**: Simular torneos completos (miles de iteraciones)
- [ ] **MLOps**: Despliegue automatizado con MLflow/Kubeflow
- [ ] **Dashboard avanzado**: Mapas de calor, pases, zonas de influencia

## 17.3 Largo Plazo (12+ meses)

- [ ] **Computer Vision**: Analizar videos de partidos para extraer datos tácticos
- [ ] **NLP para noticias**: Analizar artículos y reportes para features cualitativas
- [ ] **Modelo generativo**: Simular partidos completos con GANs
- [ ] **Multi-deporte**: Expandir a baloncesto, tenis, fútbol americano
- [ ] **Deep Learning**: Transformer para secuencias de partidos
- [ ] **Active Learning**: El sistema identifica qué partidos necesita más datos para mejorar
- [ ] **Market Making**: Modelo de cuotas justas (fair odds) comparables con casas de apuestas

---

# ANEXO A: GLOSARIO

| Término | Definición |
|---------|------------|
| **xG** | Expected Goals. Probabilidad de que un disparo se convierta en gol. |
| **xA** | Expected Assists. Probabilidad de que un pase resulte en asistencia de gol. |
| **PPDA** | Passes Per Defensive Action. Mide intensidad de presión. |
| **xGA** | Expected Goals Against. xG concedido por el equipo contrario. |
| **BTTS** | Both Teams To Score. Ambos equipos anotan. |
| **Over/Under** | Apuesta sobre si el total de goles supera o no un umbral. |
| **Elo** | Sistema de rating usado en ajedrez, adaptado para deportes. |
| **SHAP** | SHapley Additive exPlanations. Valores de contribución de cada feature. |
| **Brier Score** | Error cuadrático medio entre probabilidades predichas y resultados reales. |
| **Data Leakage** | Cuando información futura se usa para predecir el pasado. |
| **Backtesting** | Evaluar un modelo con datos históricos que no vio durante entrenamiento. |
| **Ensemble** | Combinación de múltiples modelos para mejorar precisión. |
| **Stacking** | Ensemble donde un meta-modelo aprende a combinar los modelos base. |

# ANEXO B: ÁRBOL DE DECISIÓN DE MODELOS

```
¿Qué quieres predecir?
│
├── Resultado (H/D/A)
│   ├── XGBoost (principal)
│   ├── LightGBM (alternativa)
│   └── Random Forest (benchmark)
│
├── Goles / Marcador exacto
│   └── Poisson Bivariante
│
├── Estadísticas avanzadas
│   └── LightGBM (multi-output regression)
│
├── Over/Under
│   └── Derivado de distribución Poisson
│
└── Explicación
    └── SHAP + Feature Importance
```
