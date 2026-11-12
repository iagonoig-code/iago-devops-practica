"Modelo de pedidos de la tienda online."

import uuid
from datetime import datetime
from typing import Dict

from models.producto import Producto
from models.usuario import Cliente


class Pedido:
    "Representa un pedido realizado por un cliente."

    def __init__(self, cliente: Cliente, productos: Dict[Producto, int]) -> None:
        "Inicializa un pedido asociado a un cliente y a los productos solicitados."
        "Parametros: cliente: Cliente que realiza el pedido. // productos: Diccionario {producto: cantidad} incluido en el pedido."
        
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos: Dict[Producto, int] = productos
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        "Se calcula el total del pedido sumando el precio de cada producto multiplicado por su cantidad."
        return sum(
            producto.precio * cantidad for producto, cantidad in self.productos.items()
        )

    def __str__(self) -> str:
        "Devuelve un resumen legible del pedido."
        lineas = "\n".join(
            f"    - {producto.nombre} x{cantidad} ({producto.precio:.2f}€/ud)"
            for producto, cantidad in self.productos.items()
        )
        return (
            f"Pedido [{self.id}] - Cliente: {self.cliente.nombre} "
            f"- Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{lineas}\n"
            f"    Total: {self.calcular_total():.2f}€"
        )
