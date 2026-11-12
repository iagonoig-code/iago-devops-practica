"Modelo de productos de la tienda online."

import uuid


class Producto:
    "La clase padre que representa un producto genérico de la tienda."

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        "Inicializa un producto generando un identificador único automático."
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        "Devuelve True si hay suficiente stock para la cantidad solicitada, False en caso contrario."
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        "Actualiza el stock del producto sumando o restando la cantidad especificada."
        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            raise ValueError(
                f"Stock insuficiente para '{self.nombre}': "
                f"stock actual {self.stock}, se intentó descontar {abs(cantidad)}."
            )
        self.stock = nuevo_stock

    def __str__(self) -> str:
        "Devuelve una representación legible del producto."
        return (
            f"[{self.id}] {self.nombre} - Precio: {self.precio:.2f}€ "
            f"- Stock: {self.stock}"
        )


class ProductoElectronico(Producto):
    "Producto electrónico, con meses de garantía adicionales."

    def __init__(
        self, nombre: str, precio: float, stock: int, meses_garantia: int
    ) -> None:
        "Inicializa un producto electrónico añadiendo los meses de garantía."
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        "Devuelve una representación legible incluyendo los meses de garantía."
        return f"{super().__str__()} - Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):
    "Producto de ropa, con talla y color adicionales."

    def __init__(
        self, nombre: str, precio: float, stock: int, talla: str, color: str
    ) -> None:
        "Inicializa un producto de ropa añadiendo talla y color."
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        "Devuelve una representación legible incluyendo talla y color."
        return f"{super().__str__()} - Talla: {self.talla} - Color: {self.color}"
