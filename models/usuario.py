"Modelo de usuarios de la tienda online."

import uuid


class Usuario:
    "Es la clase padre que representa a cualquier persona que interactúa con la tienda."

    def __init__(self, nombre: str, email: str) -> None:
        "Inicializa un usuario con un nombre y un correo electrónico."
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        "Devuelve True si el usuario es un administrador, False en caso contrario."
        return False

    def __str__(self) -> str:
        "Devuelve una representación legible del usuario."
        return f"[{self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    "Persona que puede realizar pedidos en la tienda."

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        "Inicializa un cliente con un nombre, correo electrónico y dirección."
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        "Devuelve una representación legible del cliente."
        return f"{super().__str__()} - Dirección: {self.direccion}"


class Administrador(Usuario):
    "Persona que gestiona la tienda."

    def is_admin(self) -> bool:
        "Los administradores siempre devuelven True."
        return True

    def __str__(self) -> str:
        "Devuelve una representación legible del administrador."
        return f"{super().__str__()} - Administrador"
