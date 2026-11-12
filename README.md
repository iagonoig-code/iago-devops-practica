# Tienda Online API – DevOps Práctica

**Autor:** Iago Novo Iglesias

## Descripción

API REST de una tienda online desarrollada en **Python** con **FastAPI** y **Pydantic**
(proyecto de la Práctica 2 de Arquitectura de Software). Permite:

- Gestionar **usuarios** (clientes y administradores).
- Gestionar **productos** (genéricos, electrónicos y ropa) y su stock.
- Crear **pedidos** de clientes, validando el stock disponible.

Los datos se guardan en memoria mientras el servidor está arrancado.
Este repositorio se usa para practicar Git/GitHub (ramas `feature/*`, Pull Requests) y Docker.

## Estructura

```
src/
  main.py      endpoints FastAPI
  schemas.py   esquemas Pydantic
  models/      clases de dominio (Usuario, Producto, Pedido)
  services/    lógica de negocio y excepciones
Dockerfile
.dockerignore
requirements.txt   dependencias con versiones fijadas
```

## Ejecución local (sin Docker)

```bash
pip install -r requirements.txt
cd src
uvicorn main:app --reload
```

## Docker

Requisito: tener [Docker](https://www.docker.com/) instalado y en marcha.

### 1. Construir la imagen

```bash
docker build -t tienda-api:1.0 .
```

### 2. Ejecutar el contenedor

```bash
# Puerto por defecto (8000)
docker run --rm -p 8000:8000 --name tienda-api tienda-api:1.0

# En segundo plano
docker run -d -p 8000:8000 --name tienda-api tienda-api:1.0

# Otro puerto del equipo (8080) y variable de entorno PORT
docker run --rm -p 8080:9000 -e PORT=9000 tienda-api:1.0
```

Para parar el contenedor en segundo plano: `docker stop tienda-api`.

### Variables de entorno

| Variable | Valor por defecto | Descripción                                   |
|----------|-------------------|-----------------------------------------------|
| `PORT`   | `8000`            | Puerto en el que escucha uvicorn dentro del contenedor. |

La aplicación no necesita secretos ni claves. Si en el futuro hicieran falta, deben pasarse
con `-e` o `--env-file`, nunca incluirse en el repositorio.

### 3. Probar que funciona

Abre la documentación interactiva en http://localhost:8000/docs (Swagger).
La salida esperada en la terminal es:

```
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Pasos de prueba (con `curl`):

```bash
# Crear un cliente  -> 201
curl -X POST http://localhost:8000/usuarios -H "Content-Type: application/json" \
  -d '{"nombre":"Luis","email":"luis@ejemplo.com","tipo":"cliente","direccion":"Calle Mayor 1"}'

# Crear un producto -> 201
curl -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
  -d '{"tipo":"generico","nombre":"Taza","precio":9.5,"stock":10}'

# Listar productos  -> 200
curl http://localhost:8000/productos
```

Con el `id` del cliente y del producto devueltos se puede crear un pedido con
`POST /pedidos` y consultarlo con `GET /usuarios/{cliente_id}/pedidos`.

### Descargar la imagen publicada (pull)

```bash
docker pull ghcr.io/iagonoig-code/iago-devops-practica:1.0
docker run --rm -p 8000:8000 ghcr.io/iagonoig-code/iago-devops-practica:1.0
```

### Publicar la imagen en un registry (GitHub Container Registry)

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u iagonoig-code --password-stdin
docker tag tienda-api:1.0 ghcr.io/iagonoig-code/iago-devops-practica:1.0
docker push ghcr.io/iagonoig-code/iago-devops-practica:1.0
```

(`GITHUB_TOKEN` es un token personal con permiso `write:packages`.)

## Flujo de trabajo Git

- `main`: rama estable, protegida; los cambios entran mediante Pull Request.
- `feature/<nombre>`: una rama por tarea, integrada en `main` con Pull Request.
