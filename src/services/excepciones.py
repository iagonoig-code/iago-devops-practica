"Excepciones de dominio de la tienda online (la capa HTTP las traduce a códigos de estado)."


class TiendaError(Exception):
    "Clase base de los errores de negocio de la tienda."


class UsuarioNoEncontradoError(TiendaError):
    "El usuario solicitado no existe."


class ProductoNoEncontradoError(TiendaError):
    "El producto solicitado no existe."


class EmailDuplicadoError(TiendaError):
    "Ya existe un usuario registrado con ese email."


class UsuarioNoEsClienteError(TiendaError):
    "El usuario existe pero no es un cliente, por lo que no puede realizar pedidos."


class StockInsuficienteError(TiendaError):
    "No hay stock suficiente para atender la cantidad solicitada de un producto."
