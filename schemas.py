"""Esquemas Pydantic de la API: validan las peticiones y dan forma a las respuestas.

Cada esquema de lectura incluye un método `desde_dominio` que convierte un objeto de las
clases de dominio (Practica 1) en el esquema que se devuelve al cliente."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.pedido import Pedido
from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Cliente, Usuario

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# Usuarios
class UsuarioCreate(BaseModel):
    "Datos necesarios para crear un usuario."

    nombre: str = Field(..., min_length=1, max_length=100, examples=["Luis Pousa"])
    email: str = Field(..., pattern=EMAIL_REGEX, examples=["luis@ejemplo.com"])
    tipo: Literal["cliente", "administrador"] = Field(..., examples=["cliente"])
    direccion: Optional[str] = Field(
        default=None, max_length=200, examples=["Calle Marqués de Amboage 11, Coruña"]
    )

    @model_validator(mode="after")
    def validar_direccion(self) -> "UsuarioCreate":
        "Los clientes necesitan una dirección postal."
        if self.tipo == "cliente" and not (self.direccion and self.direccion.strip()):
            raise ValueError("La dirección es obligatoria para los usuarios de tipo 'cliente'.")
        return self


class UsuarioRead(BaseModel):
    "Información de un usuario devuelta al cliente."

    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    email: str
    es_admin: bool

    @classmethod
    def desde_dominio(cls, usuario: Usuario) -> "UsuarioRead":
        return cls(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin(),
        )


# Productos
class ProductoCreate(BaseModel):
    "Datos necesarios para crear un producto; los atributos extra dependen del tipo."

    tipo: Literal["generico", "electronico", "ropa"] = Field(..., examples=["electronico"])
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Switch 2"])
    precio: float = Field(..., gt=0, examples=[499.0])
    stock: int = Field(..., ge=0, examples=[10])
    meses_garantia: Optional[int] = Field(default=None, ge=0, examples=[36])
    talla: Optional[str] = Field(default=None, min_length=1, examples=["XL"])
    color: Optional[str] = Field(default=None, min_length=1, examples=["Morado"])

    @model_validator(mode="after")
    def validar_atributos_por_tipo(self) -> "ProductoCreate":
        "Comprueba que vienen los atributos obligatorios de cada tipo y ninguno ajeno."
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("'meses_garantia' es obligatorio para productos electrónicos.")
            if self.talla is not None or self.color is not None:
                raise ValueError("Un producto electrónico no admite 'talla' ni 'color'.")
        elif self.tipo == "ropa":
            if self.talla is None or self.color is None:
                raise ValueError("'talla' y 'color' son obligatorios para productos de ropa.")
            if self.meses_garantia is not None:
                raise ValueError("Un producto de ropa no admite 'meses_garantia'.")
        else:  # generico
            if any(v is not None for v in (self.meses_garantia, self.talla, self.color)):
                raise ValueError(
                    "Un producto genérico no admite 'meses_garantia', 'talla' ni 'color'."
                )
        return self


class ProductoRead(BaseModel):
    "Información de un producto devuelta al cliente (atributos opcionales según el tipo)."

    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def desde_dominio(cls, producto: Producto) -> "ProductoRead":
        datos = dict(
            id=producto.id,
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
        )
        if isinstance(producto, ProductoElectronico):
            return cls(tipo="electronico", meses_garantia=producto.meses_garantia, **datos)
        if isinstance(producto, ProductoRopa):
            return cls(tipo="ropa", talla=producto.talla, color=producto.color, **datos)
        return cls(tipo="generico", **datos)


# Pedidos
class PedidoItemCreate(BaseModel):
    "Línea de pedido en la petición: un producto y su cantidad."

    producto_id: str = Field(..., min_length=1)
    cantidad: int = Field(..., gt=0, examples=[2])


class PedidoCreate(BaseModel):
    "Datos necesarios para crear un pedido."

    cliente_id: str = Field(..., min_length=1)
    items: List[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    "Línea de pedido en la respuesta."

    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    "Pedido completo devuelto al cliente."

    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: List[PedidoItemRead]

    @classmethod
    def desde_dominio(cls, pedido: Pedido) -> "PedidoRead":
        items = [
            PedidoItemRead(
                producto_id=producto.id,
                nombre=producto.nombre,
                precio_unitario=producto.precio,
                cantidad=cantidad,
                subtotal=round(producto.precio * cantidad, 2),
            )
            for producto, cantidad in pedido.productos.items()
        ]
        return cls(
            id=pedido.id,
            fecha=pedido.fecha,
            cliente_id=pedido.cliente.id,
            cliente_nombre=pedido.cliente.nombre,
            total=round(pedido.calcular_total(), 2),
            items=items,
        )
