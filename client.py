"""
Cliente Blackjack - Interfaz para que los jugadores se conecten y jueguen
"""
import socket
import json
import threading



class ClienteBlackjack:
    def __init__(self, host='localhost', puerto=5555):
        self.host = host
        self.puerto = puerto
        self.socket = None
        self.id_jugador = None
        self.nombre = None
        self.conectado = False
        self.estado_juego = None
        self._recv_buffer = ""

    def conectar(self, nombre):
        """Conecta al servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            self.nombre = nombre
            self.conectado = True

            # Enviar registro
            mensaje = {
                'tipo': 'registro',
                'nombre': nombre
            }
            self.socket.send(json.dumps(mensaje).encode('utf-8'))

            # Recibir confirmación
            # Leer hasta el terminador '\n' para obtener un JSON completo
            datos = self._recv_line()
            respuesta = json.loads(datos) if datos else None

            if respuesta['tipo'] == 'registro_confirmado':
                self.id_jugador = respuesta['id_jugador']
                print(f"\n✓ {respuesta['mensaje']}")
                return True
            else:
                print("Error en el registro")
                return False

        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            return False

    def iniciar_receptor(self):
        """Inicia thread para recibir mensajes del servidor"""
        thread_receptor = threading.Thread(target=self.recibir_mensajes)
        thread_receptor.daemon = True
        thread_receptor.start()

    def recibir_mensajes(self):
        """Recibe mensajes del servidor"""
        while self.conectado:
            try:
                # Leer líneas terminadas en '\n' y procesar cada JSON por separado
                datos = self.socket.recv(1024).decode('utf-8')
                if not datos:
                    break

                self._recv_buffer += datos

                while '\n' in self._recv_buffer:
                    linea, self._recv_buffer = self._recv_buffer.split('\n', 1)
                    if not linea.strip():
                        continue
                    try:
                        mensaje = json.loads(linea)
                        self.procesar_mensaje_servidor(mensaje)
                    except json.JSONDecodeError:
                        print("Error decodificando JSON recibido")

            except Exception as e:
                if self.conectado:
                    print(f"Error recibiendo mensaje: {e}")
                break

    def procesar_mensaje_servidor(self, mensaje):
        """Procesa los mensajes recibidos del servidor"""
        tipo = mensaje.get('tipo')

        if tipo == 'actualización_estado':
            self.estado_juego = mensaje['estado_juego']
            self.mostrar_estado_juego()

        elif tipo == 'resultado_ronda':
            self.estado_juego = mensaje['estado_juego']
            resultado = mensaje['resultado']
            ganancia = mensaje['ganancia']
            self.mostrar_resultado_ronda(resultado, ganancia)

        elif tipo == 'error':
            print(f"\n❌ Error: {mensaje['mensaje']}")

    def mostrar_estado_juego(self):
        """Muestra el estado actual del juego"""
        if not self.estado_juego:
            return

        print("\n" + "=" * 60)
        print("ESTADO DEL JUEGO")
        print("=" * 60)

        # Mostrar crupier
        crupier = self.estado_juego['crupier']
        print(f"\nCrupier: {crupier['mano']} Estado: {crupier['estado']}")

        # Mostrar jugadores
        print("\nJugadores:")
        for id_j, jugador in self.estado_juego['jugadores'].items():
            marcador = "→" if id_j == self.id_jugador else " "
            print(f"{marcador} {jugador['nombre']}: {jugador['mano']}")
            print(f"   Estado: {jugador['estado']} | Apuesta: {jugador['apuesta']} | Dinero: {jugador['dinero']}")

        print("=" * 60)

    def mostrar_resultado_ronda(self, resultado, ganancia):
        """Muestra el resultado de la ronda"""
        print("\n" + "=" * 60)
        print("RESULTADO DE LA RONDA")
        print("=" * 60)

        if resultado == "ganador":
            print(f"✓ ¡GANASTE! +{ganancia} fichas")
        elif resultado == "perdedor":
            print(f"✗ Perdiste")
        elif resultado == "empate":
            print(f"= EMPATE. Recuperas tu apuesta: {ganancia} fichas")

        print("=" * 60)

    def hacer_apuesta(self, cantidad):
        """Realiza una apuesta"""
        mensaje = {
            'tipo': 'apuesta',
            'cantidad': cantidad
        }
        self.socket.send(json.dumps(mensaje).encode('utf-8'))
        print(f"Apuesta de {cantidad} realizada")

    def pedir_carta(self):
        """Pide una carta"""
        mensaje = {
            'tipo': 'pedir'
        }
        self.socket.send(json.dumps(mensaje).encode('utf-8'))

    def plantarse(self):
        """Se planta"""
        mensaje = {
            'tipo': 'plantarse'
        }
        self.socket.send(json.dumps(mensaje).encode('utf-8'))

    def _recv_line(self):
        """Lee desde el socket hasta encontrar '\n' y devuelve la línea (sin '\n').
        Este método utiliza self._recv_buffer para acumular datos entre llamadas."""
        # Intentar ver si ya hay una línea completa en el buffer
        if '\n' in self._recv_buffer:
            linea, self._recv_buffer = self._recv_buffer.split('\n', 1)
            return linea

        # De lo contrario, leer desde el socket hasta obtener '\n'
        while True:
            datos = self.socket.recv(1024).decode('utf-8')
            if not datos:
                return None
            self._recv_buffer += datos
            if '\n' in self._recv_buffer:
                linea, self._recv_buffer = self._recv_buffer.split('\n', 1)
                return linea

    def solicitar_nueva_ronda(self):
        """Solicita una nueva ronda"""
        mensaje = {
            'tipo': 'nueva_ronda'
        }
        self.socket.send(json.dumps(mensaje).encode('utf-8'))

    def solicitar_estado(self):
        """Solicita el estado del juego"""
        mensaje = {
            'tipo': 'estado'
        }
        self.socket.send(json.dumps(mensaje).encode('utf-8'))

    def desconectar(self):
        """Se desconecta del servidor"""
        self.conectado = False
        if self.socket:
            self.socket.close()
        print("Desconectado del servidor")

    def menu_principal(self):
        """Menú principal del cliente"""
        print("\n" + "=" * 60)
        print("BLACKJACK MULTIJUGADOR")
        print("=" * 60)

        while self.conectado:
            print("\nOpciones:")
            print("1. Hacer apuesta")
            print("2. Pedir carta")
            print("3. Plantarse")
            print("4. Ver estado del juego")
            print("5. Nueva ronda")
            print("6. Salir")

            opcion = input("\nSelecciona una opción (1-6): ").strip()

            if opcion == '1':
                try:
                    cantidad = int(input("Cantidad a apostar: "))
                    self.hacer_apuesta(cantidad)
                except ValueError:
                    print("Cantidad inválida")

            elif opcion == '2':
                self.pedir_carta()

            elif opcion == '3':
                self.plantarse()

            elif opcion == '4':
                self.solicitar_estado()

            elif opcion == '5':
                self.solicitar_nueva_ronda()

            elif opcion == '6':
                self.desconectar()
                break

            else:
                print("Opción inválida")


def main():
    """Función principal"""
    # Solicitar IP del servidor
    print("=" * 60)
    print("CLIENTE BLACKJACK")
    print("=" * 60)

    host = input("IP del servidor (por defecto localhost): ").strip()
    if not host:
        host = 'localhost'

    try:
        puerto = int(input("Puerto del servidor (por defecto 5555): ").strip())
    except ValueError:
        puerto = 5555

    # Crear cliente
    cliente = ClienteBlackjack(host, puerto)

    # Conectar
    nombre = input("Tu nombre: ").strip()
    if not nombre:
        nombre = "Jugador"

    if cliente.conectar(nombre):
        # Iniciar receptor de mensajes
        cliente.iniciar_receptor()

        # Mostrar menú principal
        cliente.menu_principal()
    else:
        print("No se pudo conectar al servidor")


if __name__ == '__main__':
    main()

