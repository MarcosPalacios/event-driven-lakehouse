# Event-Driven Lakehouse

Proyecto práctico enfocado en una plataforma de datos moderna sobre AWS con arquitectura Bronze/Silver/Gold.

## Objetivo

Crear una solución con:

- Ingestión incremental y idempotente desde GitHub Events
- Almacenamiento en S3 Bronze/Silver/Gold
- Procesamiento serverless con Lambda
- Query layer con Athena
- Transformaciones con dbt
- Orquestación con Airflow
- Infraestructura declarativa con Terraform
- Observabilidad con CloudWatch

## Estructura del repo

```
event-driven-lakehouse/
│
├── ingestion/
├── lambda/
├── dbt/
├── airflow/
├── terraform/
├── docs/
├── tests/
└── README.md
```

## Siguientes pasos

1. Definir el flujo de ingestión incremental y los eventos de GitHub.
2. Prototipar el script de `ingestion/` para descargar y guardar JSONL en S3 Bronze.
3. Desarrollar la Lambda en `lambda/` con separación entre handler y lógica de negocio.
4. Crear modelos dbt en `dbt/` con `incremental`, `tests`, `dedup` y métricas.
5. Añadir DAGs de Airflow en `airflow/` para orquestar ingestion, dbt runs y tests.
6. Migrar la infraestructura AWS a `terraform/` paso a paso.
7. Documentar el diseño, diagramas y decisiones en `docs/`.
