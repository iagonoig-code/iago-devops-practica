"""Punto de entrada de la API REST de la tienda online (capa de exposición del servicio).
 
Práctica 2 - Arquitectura de Software (FastAPI + Pydantic).
 
Ejecución: (desde la carpeta que contiene este archivo):
    pip install -r requirements.txt
    uvicorn main:app --reload
    Swagger: http://127.0.0.1:8000/docs  (los datos viven en la memoria mientras el servidor esté arrancado)
 
Estructrura:
    models/                    clases de dominio de la Práctica 1 (sin cambios)
    services/tienda_service.py  lógica de negocio; lanza excepciones (services/excepciones.py)
    schemas.py                 esquemas Pydantic (Usuario, Producto y Pedido: Create/Read)
    main.py                    endpoints FastAPI
 
CÓDIGOS HTTP:
    201 recurso creado // 204 producto eliminado
    404 usuario/producto inexistente
    409 email duplicado o stock insuficiente
    403 el usuario del pedido no es cliente
    422 datos inválidos (email, atributos según tipo, cantidad <= 0, etc.)
"""

from typing import Dict, List

from fastapi import FastAPI, HTTPException, Response, status

from schemas import (
    PedidoCreate,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
)
from services.excepciones import (
    EmailDuplicadoError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    UsuarioNoEncontradoError,
    UsuarioNoEsClienteError,
)
from services.tienda_service import TiendaService

app = FastAPI(
    title="Tienda online API",
    description="API REST de la tienda online (Práctica 2 - Arquitectura de Software).",
    version="1.0.0",
)

# Única instancia del servicio: los datos viven en memoria mientras el servidor esté arrancado.
tienda = TiendaService()


# Usuarios
@app.post(
    "/usuarios",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
    summary="Crea un nuevo usuario",
)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    try:
        usuario = tienda.registrar_usuario(
            datos.tipo, datos.nombre, datos.email, direccion=datos.direccion
        )
    except EmailDuplicadoError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return UsuarioRead.desde_dominio(usuario)


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRead,
    tags=["Usuarios"],
    summary="Devuelve un usuario concreto",
)
def obtener_usuario(usuario_id: str) -> UsuarioRead:
    try:
        return UsuarioRead.desde_dominio(tienda.obtener_usuario(usuario_id))
    except UsuarioNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(
    "/usuarios",
    response_model=List[UsuarioRead],
    tags=["Usuarios"],
    summary="Devuelve la lista de usuarios registrados",
)
def listar_usuarios() -> List[UsuarioRead]:
    return [UsuarioRead.desde_dominio(u) for u in tienda.listar_usuarios()]


# Productos
@app.post(
    "/productos",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
    summary="Crea un nuevo producto",
)
def crear_producto(datos: ProductoCreate) -> ProductoRead:
    producto = tienda.agregar_producto(
        datos.tipo,
        datos.nombre,
        datos.precio,
        datos.stock,
        meses_garantia=datos.meses_garantia,
        talla=datos.talla,
        color=datos.color,
    )
    return ProductoRead.desde_dominio(producto)


@app.get(
    "/productos",
    response_model=List[ProductoRead],
    tags=["Productos"],
    summary="Devuelve la lista de productos",
)
def listar_productos() -> List[ProductoRead]:
    return [ProductoRead.desde_dominio(p) for p in tienda.listar_productos()]


@app.get(
    "/productos/{producto_id}",
    response_model=ProductoRead,
    tags=["Productos"],
    summary="Devuelve un producto concreto",
)
def obtener_producto(producto_id: str) -> ProductoRead:
    try:
        return ProductoRead.desde_dominio(tienda.obtener_producto(producto_id))
    except ProductoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Productos"],
    summary="Elimina un producto",
)
def eliminar_producto(producto_id: str) -> Response:
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El producto '{producto_id}' no existe.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Pedidos
@app.post(
    "/pedidos",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Pedidos"],
    summary="Crea un pedido",
)
def crear_pedido(datos: PedidoCreate) -> PedidoRead:
    # Si un mismo producto aparece en varias líneas, se suman sus cantidades.
    solicitados: Dict[str, int] = {}
    for item in datos.items:
        solicitados[item.producto_id] = solicitados.get(item.producto_id, 0) + item.cantidad

    try:
        pedido = tienda.realizar_pedido(datos.cliente_id, solicitados)
    except (UsuarioNoEncontradoError, ProductoNoEncontradoError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UsuarioNoEsClienteError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except StockInsuficienteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return PedidoRead.desde_dominio(pedido)


@app.get(
    "/usuarios/{cliente_id}/pedidos",
    response_model=List[PedidoRead],
    tags=["Pedidos"],
    summary="Devuelve los pedidos de un cliente",
)
def listar_pedidos_cliente(cliente_id: str) -> List[PedidoRead]:
    try:
        tienda.obtener_usuario(cliente_id)
    except UsuarioNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return [PedidoRead.desde_dominio(p) for p in tienda.listar_pedidos_usuario(cliente_id)]
