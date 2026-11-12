# Tienda Online API – DevOps Práctica

**Autor:** Iago Novo Iglesias

## Descripción

API REST de una tienda online desarrollada en **Python** con **FastAPI** y **Pydantic**
(proyecto de la Práctica 2 de Arquitectura de Software). Permite:

- Gestionar **usuarios** (clientes y administradores).
- Gestionar **productos** (genéricos, electrónicos y ropa) y su stock.
- Crear **pedidos** de clientes, validando el stock disponible.

Los datos se guardan en memoria mientras el servidor está arrancado.
Este repositorio se usa para practicar control de versiones (Git/GitHub),
ramas `feature/*`, Pull Requests y, más adelante, contenedores Docker y CI/CD.

## Estructura

```
models/      clases de dominio (Usuario, Producto, Pedido)
services/    lógica de negocio y excepciones
schemas.py   esquemas Pydantic
main.py      endpoints FastAPI
```

## Ejecución local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Documentación Swagger: http://127.0.0.1:8000/docs

## Flujo de trabajo Git

- `main`: rama estable.
- `feature/<nombre>`: una rama por tarea, integrada en `main` mediante Pull Request.
