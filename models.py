"""Clases que representan las entidades del dominio (POO)."""


class Piloto:
    def __init__(self, id, nombre, apellido, nacionalidad, edad):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.nacionalidad = nacionalidad
        self.edad = edad

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def categoria(self):
        """Clasifica al piloto segun su edad."""
        if self.edad < 25:
            return "Junior"
        elif self.edad <= 35:
            return "Senior"
        return "Veterano"


class Monoplaza:
    def __init__(self, id, modelo, motor, potencia, id_piloto,
                 piloto_nombre=None, piloto_apellido=None):
        self.id = id
        self.modelo = modelo
        self.motor = motor
        self.potencia = potencia
        self.id_piloto = id_piloto
        self.piloto_nombre = piloto_nombre
        self.piloto_apellido = piloto_apellido

    def es_alta_potencia(self, umbral=850):
        return self.potencia >= umbral

    def piloto_asignado(self):
        if self.piloto_nombre:
            return f"{self.piloto_nombre} {self.piloto_apellido}"
        return "Sin asignar"


class Circuito:
    def __init__(self, id, nombre_gp, pais, longitud_km, tipo_pista):
        self.id = id
        self.nombre_gp = nombre_gp
        self.pais = pais
        self.longitud_km = longitud_km
        self.tipo_pista = tipo_pista

    def es_largo(self, umbral=5.5):
        """True si el circuito supera el umbral en km."""
        return self.longitud_km > umbral

    def clasificacion_longitud(self):
        return "Largo" if self.es_largo() else "Corto"
