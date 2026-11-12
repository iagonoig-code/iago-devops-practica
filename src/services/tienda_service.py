"Capa de servicios que centraliza las operaciones de la tienda online."

from typing import Dict, List

from models.pedido import Pedido
from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Administrador, Cliente, Usuario
from services.excepciones import (
    EmailDuplicadoError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    UsuarioNoEncontradoError,
    UsuarioNoEsClienteError,
)


class TiendaService:
    "Intermediario entre los usuarios y los productos de la tienda."

    def __init__(self) -> None:
        "Inicializa los almacenes en memoria de usuarios, productos y pedidos."
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []


    # Usuarios
    
    def registrar_usuario(self, tipo: str, nombre: str, email: str, **kwargs) -> Usuario:
        "Registra un nuevo usuario en la tienda." 
        """Parametros: tipo: "cliente" o "administrador". // nombre: Nombre del usuario. // email: Correo electrónico del usuario. 
        // **kwargs: Argumentos adicionales según el tipo (p. ej. direccion). // Returns: La instancia de Usuario (o subclase) creada."""
    
        if any(u.email.lower() == email.lower() for u in self.usuarios.values()):
            raise EmailDuplicadoError(f"Ya existe un usuario con el email '{email}'.")

        if tipo == "cliente":
            direccion = kwargs.get("direccion", "")
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError(f"Tipo de usuario desconocido: {tipo}")

        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: str) -> Usuario:
        "Devuelve un usuario por su id o lanza UsuarioNoEncontradoError si no existe."
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontradoError(f"El usuario '{usuario_id}' no existe.")
        return usuario

    def listar_usuarios(self) -> List[Usuario]:
        "Devuelve la lista de todos los usuarios registrados."
        return list(self.usuarios.values())

    # Productos
    def agregar_producto(
        self, tipo: str, nombre: str, precio: float, stock: int, **kwargs
    ) -> Producto:
        "Añade un producto de una categoría concreta al inventario."
        """ Parametros: tipo: "electronico", "ropa" o "generico". // nombre: Nombre del producto. // precio: Precio unitario del producto."""
        "// stock: Cantidad inicial de stock. // **kwargs: Argumentos adicionales según el tipo (meses_garantia para electrónicos, talla/color para ropa)."

        "Devuelve: La instancia de Producto (o subclase) creada."
        
        if tipo == "electronico":
            meses_garantia = kwargs.get("meses_garantia", 0)
            producto: Producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
        elif tipo == "ropa":
            talla = kwargs.get("talla", "")
            color = kwargs.get("color", "")
            producto = ProductoRopa(nombre, precio, stock, talla, color)
        elif tipo == "generico":
            producto = Producto(nombre, precio, stock)
        else:
            raise ValueError(f"Tipo de producto desconocido: {tipo}")

        self.productos[producto.id] = producto
        return producto

    def obtener_producto(self, producto_id: str) -> Producto:
        "Devuelve un producto por su id o lanza ProductoNoEncontradoError si no existe."
        producto = self.productos.get(producto_id)
        if producto is None:
            raise ProductoNoEncontradoError(f"El producto '{producto_id}' no existe.")
        return producto

    def eliminar_producto(self, producto_id: str) -> bool:
        "Elimina un producto del inventario a partir de su identificador."

        "Devuelve: True si el producto existía y se eliminó, False en caso contrario."
        
        if producto_id in self.productos:
            del self.productos[producto_id]
            return True
        return False

    def listar_productos(self) -> List[Producto]:
        "Devuelve la lista de todos los productos disponibles en la tienda."
        return list(self.productos.values())


    # Pedidos

    def realizar_pedido(
        self, usuario_id: str, productos_solicitados: Dict[str, int]
    ) -> Pedido:
        """Realiza un pedido para un cliente si existe y hay stock suficiente.

        Parametros: usuario_id: identificador del usuario (debe ser un Cliente).
        productos_solicitados: diccionario {producto_id: cantidad}.

        Devuelve el Pedido creado. Lanza UsuarioNoEncontradoError, UsuarioNoEsClienteError,
        ProductoNoEncontradoError o StockInsuficienteError si no se puede completar; en ese
        caso no se modifica el stock de ningún producto."""

        usuario = self.obtener_usuario(usuario_id)
        if not isinstance(usuario, Cliente):
            raise UsuarioNoEsClienteError(
                f"El usuario '{usuario_id}' no es un cliente y no puede realizar pedidos."
            )

        productos_pedido: Dict[Producto, int] = {}
        for producto_id, cantidad in productos_solicitados.items():
            producto = self.obtener_producto(producto_id)
            if not producto.hay_stock(cantidad):
                raise StockInsuficienteError(
                    f"Stock insuficiente de '{producto.nombre}' "
                    f"(disponible: {producto.stock}, solicitado: {cantidad})."
                )
            productos_pedido[producto] = cantidad

        # Todo correcto: descontamos stock y generamos el pedido
        for producto, cantidad in productos_pedido.items():
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> List[Pedido]:
        "Lista todos los pedidos de un usuario, ordenados por fecha."
        pedidos_usuario = [p for p in self.pedidos if p.cliente.id == usuario_id]
        return sorted(pedidos_usuario, key=lambda p: p.fecha)
