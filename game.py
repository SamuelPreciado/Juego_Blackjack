"""
Módulo de lógica del juego Blackjack
"""
from deck import Baraja


class Mano:
    def __init__(self):
        self.cartas = []

    def agregar_carta(self, carta):
        """Agrega una carta a la mano"""
        self.cartas.append(carta)

    def calcular_valor(self):
        """Calcula el valor de la mano considerando los aces"""
        valor = 0
        aces = 0

        for carta in self.cartas:
            if carta.valor == 'A':
                aces += 1
                valor += 11
            else:
                valor += carta.get_valor_numerico()

        # Ajusta los aces si es necesario
        while valor > 21 and aces > 0:
            valor -= 10
            aces -= 1

        return valor

    def es_blackjack(self):
        """Verifica si es blackjack (21 con 2 cartas)"""
        return len(self.cartas) == 2 and self.calcular_valor() == 21

    def esta_busted(self):
        """Verifica si se pasó de 21"""
        return self.calcular_valor() > 21

    def __str__(self):
        return f"{', '.join(str(c) for c in self.cartas)} (Valor: {self.calcular_valor()})"


class Jugador:
    def __init__(self, id_jugador, nombre):
        self.id_jugador = id_jugador
        self.nombre = nombre
        self.mano = Mano()
        self.apuesta = 0
        self.estado = "esperando"  # esperando, jugando, plantado, busted, ganador, perdedor
        self.dinero = 1000  # Dinero inicial

    def nueva_mano(self):
        """Inicia una nueva mano"""
        self.mano = Mano()
        self.estado = "jugando"

    def plantarse(self):
        """El jugador se planta"""
        self.estado = "plantado"

    def hacer_apuesta(self, cantidad):
        """El jugador hace una apuesta"""
        if cantidad > self.dinero:
            return False
        self.apuesta = cantidad
        self.dinero -= cantidad
        return True

    def resetear_para_nueva_ronda(self):
        """Prepara el jugador para una nueva ronda"""
        self.mano = Mano()
        self.apuesta = 0
        self.estado = "esperando"

    def __str__(self):
        return f"{self.nombre}: {self.mano}"


class Crupier:
    def __init__(self):
        self.mano = Mano()
        self.estado = "esperando"

    def nueva_mano(self):
        """Inicia una nueva mano"""
        self.mano = Mano()
        self.estado = "jugando"

    def debe_pedir_carta(self):
        """Determina si el crupier debe pedir más cartas (debe llegar a 17 o más)"""
        return self.mano.calcular_valor() < 17

    def plantarse(self):
        """El crupier se planta"""
        self.estado = "plantado"

    def resetear(self):
        """Resetea el crupier para una nueva ronda"""
        self.mano = Mano()
        self.estado = "esperando"

    def __str__(self):
        return f"Crupier: {self.mano}"


class Juego:
    def __init__(self):
        self.baraja = Baraja(numero_mazos=6)
        self.crupier = Crupier()
        self.jugadores = {}
        self.ronda_activa = False
        self.fase = "apuestas"  # apuestas, repartiendo, jugando, resultados

    def agregar_jugador(self, id_jugador, nombre):
        """Agrega un jugador al juego"""
        jugador = Jugador(id_jugador, nombre)
        self.jugadores[id_jugador] = jugador
        return jugador

    def obtener_jugador(self, id_jugador):
        """Obtiene un jugador por su ID"""
        return self.jugadores.get(id_jugador)

    def iniciar_ronda(self):
        """Inicia una nueva ronda"""
        self.fase = "apuestas"
        self.ronda_activa = True

        for jugador in self.jugadores.values():
            jugador.resetear_para_nueva_ronda()

        self.crupier.resetear()

    def repartir_cartas(self):
        """Reparte 2 cartas a cada jugador y al crupier"""
        self.fase = "repartiendo"

        # Repartir 2 cartas a cada jugador
        for jugador in self.jugadores.values():
            jugador.nueva_mano()
            jugador.mano.agregar_carta(self.baraja.sacar_carta())
            jugador.mano.agregar_carta(self.baraja.sacar_carta())

        # Repartir 2 cartas al crupier
        self.crupier.nueva_mano()
        self.crupier.mano.agregar_carta(self.baraja.sacar_carta())
        self.crupier.mano.agregar_carta(self.baraja.sacar_carta())

        self.fase = "jugando"

    def pedir_carta(self, id_jugador):
        """El jugador pide una carta"""
        jugador = self.jugadores.get(id_jugador)
        if not jugador:
            return False

        jugador.mano.agregar_carta(self.baraja.sacar_carta())

        if jugador.mano.esta_busted():
            jugador.estado = "busted"
            return False

        return True

    def plantarse_jugador(self, id_jugador):
        """El jugador se planta"""
        jugador = self.jugadores.get(id_jugador)
        if jugador:
            jugador.plantarse()
            return True
        return False

    def jugar_crupier(self):
        """El crupier juega según las reglas (llega a 17 o más)"""
        while self.crupier.debe_pedir_carta():
            self.crupier.mano.agregar_carta(self.baraja.sacar_carta())

        self.crupier.plantarse()

    def determinar_ganadores(self):
        """Determina los ganadores de la ronda"""
        resultados = {}
        valor_crupier = self.crupier.mano.calcular_valor()
        crupier_busted = self.crupier.mano.esta_busted()

        for id_jugador, jugador in self.jugadores.items():
            valor_jugador = jugador.mano.calcular_valor()

            if jugador.mano.esta_busted():
                jugador.estado = "perdedor"
                resultados[id_jugador] = ("perdedor", 0)
            elif crupier_busted:
                jugador.estado = "ganador"
                resultados[id_jugador] = ("ganador", jugador.apuesta * 2)
                jugador.dinero += jugador.apuesta * 2
            elif valor_jugador > valor_crupier:
                jugador.estado = "ganador"
                resultados[id_jugador] = ("ganador", jugador.apuesta * 2)
                jugador.dinero += jugador.apuesta * 2
            elif valor_jugador == valor_crupier:
                jugador.estado = "empate"
                resultados[id_jugador] = ("empate", jugador.apuesta)
                jugador.dinero += jugador.apuesta
            else:
                jugador.estado = "perdedor"
                resultados[id_jugador] = ("perdedor", 0)

        return resultados

    def obtener_estado_juego(self):
        """Retorna el estado actual del juego"""
        return {
            "fase": self.fase,
            "ronda_activa": self.ronda_activa,
            "jugadores": {
                id_j: {
                    "nombre": j.nombre,
                    "mano": str(j.mano),
                    "valor": j.mano.calcular_valor(),
                    "estado": j.estado,
                    "apuesta": j.apuesta,
                    "dinero": j.dinero
                }
                for id_j, j in self.jugadores.items()
            },
            "crupier": {
                "mano": str(self.crupier.mano),
                "valor": self.crupier.mano.calcular_valor(),
                "estado": self.crupier.estado
            }
        }

