"""
Módulo para manejar la baraja de cartas
"""
import random
from enum import Enum


class Palo(Enum):
    PICAS = "♠"
    CORAZONES = "♥"
    DIAMANTES = "♦"
    TRÉBOLES = "♣"


class Carta:
    def __init__(self, valor, palo):
        self.valor = valor
        self.palo = palo
    def get_imagen_archivo(self):
        """Retorna el nombre del archivo de imagen de la carta.

        Formato: {valor}_of_{palo}.png
        Ejemplo: ace_of_spades.png, 10_of_hearts.png
        """
        # Mapear valor a nombre de archivo
        valor_map = {
            'A': 'ace',
            'J': 'jack',
            'Q': 'queen',
            'K': 'king'
        }
        valor_str = valor_map.get(self.valor, self.valor)

        # Mapear palo a nombre en inglés
        palo_map = {
            'PICAS': 'spades',
            'CORAZONES': 'hearts',
            'DIAMANTES': 'diamonds',
            'TRÉBOLES': 'clubs'
        }
        palo_str = palo_map.get(self.palo.name, 'unknown')

        return f"{valor_str}_of_{palo_str}.png"


    def get_valor_numerico(self):
        """Retorna el valor numérico de la carta"""
        if self.valor in ['J', 'Q', 'K']:
            return 10
        elif self.valor == 'A':
            return 11
        else:
            return int(self.valor)

    def __str__(self):
        return f"{self.valor}{self.palo.value}"

    def __repr__(self):
        return str(self)


class Baraja:
    def __init__(self, numero_mazos=1):
        self.numero_mazos = numero_mazos
        self.cartas = []
        self.inicializar()

    def inicializar(self):
        """Inicializa la baraja con todas las cartas"""
        self.cartas = []
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

        for _ in range(self.numero_mazos):
            for palo in Palo:
                for valor in valores:
                    self.cartas.append(Carta(valor, palo))

        self.mezclar()

    def mezclar(self):
        """Mezcla la baraja"""
        random.shuffle(self.cartas)

    def sacar_carta(self):
        """Saca una carta de la baraja"""
        if len(self.cartas) < 10:  # Si quedan pocas cartas, reinicializar
            self.inicializar()
        return self.cartas.pop()

    def cantidad_cartas(self):
        """Retorna la cantidad de cartas restantes"""
        return len(self.cartas)

