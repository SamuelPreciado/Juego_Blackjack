"""
Servidor principal del juego Blackjack multijugador
Gestiona las conexiones de clientes y la lógica del juego
"""
import socket
import threading
import json
import time
from game import Juego


class ServidorBlackjack:
    def __init__(self, host='0.0.0.0', puerto=5555):
        self.host = host
        self.puerto = puerto
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientes = {}  # {id_conexion: {'socket': socket, 'nombre': nombre, 'id_jugador': id}}
        self.id_siguiente = 0
        self.lock = threading.Lock()
        self.juego = Juego()
        self.running = True

    def iniciar(self):
        """Inicia el servidor"""
        self.servidor.bind((self.host, self.puerto))
        self.servidor.listen(5)
        print(f"Servidor iniciado en {self.host}:{self.puerto}")
        print("Esperando conexiones de jugadores...")

        try:
            while self.running:
                try:
                    cliente_socket, direccion = self.servidor.accept()
                    print(f"Nueva conexión desde {direccion}")

                    # Crear thread para manejar el cliente
                    thread_cliente = threading.Thread(
                        target=self.manejar_cliente,
                        args=(cliente_socket, direccion)
                    )
                    thread_cliente.daemon = True
                    thread_cliente.start()
                except Exception as e:
                    print(f"Error aceptando conexión: {e}")
        except KeyboardInterrupt:
            print("\nServidor detenido.")
        finally:
            self.cerrar()

    def manejar_cliente(self, cliente_socket, direccion):
        """Maneja la comunicación con un cliente"""
        id_conexion = None
        id_jugador = None

        try:
            # Recibir nombre del jugador
            datos = cliente_socket.recv(1024).decode('utf-8')
            mensaje = json.loads(datos)

            if mensaje['tipo'] != 'registro':
                return

            nombre = mensaje['nombre']

            with self.lock:
                id_conexion = self.id_siguiente
                self.id_siguiente += 1
                id_jugador = id_conexion

                # Agregar jugador al juego
                self.juego.agregar_jugador(id_jugador, nombre)
                self.clientes[id_conexion] = {
                    'socket': cliente_socket,
                    'nombre': nombre,
                    'id_jugador': id_jugador
                }

            print(f"Jugador '{nombre}' registrado (ID: {id_jugador})")

            # Enviar confirmación de registro
            respuesta = {
                'tipo': 'registro_confirmado',
                'id_jugador': id_jugador,
                'mensaje': f'Bienvenido {nombre}'
            }
            cliente_socket.send(json.dumps(respuesta).encode('utf-8'))

            # Bucle principal de comunicación
            while self.running:
                datos = cliente_socket.recv(1024).decode('utf-8')

                if not datos:
                    break

                try:
                    mensaje = json.loads(datos)
                    self.procesar_mensaje(id_jugador, mensaje)
                except json.JSONDecodeError:
                    print(f"Error decodificando mensaje de {nombre}")

        except Exception as e:
            print(f"Error con cliente {nombre}: {e}")
        finally:
            with self.lock:
                if id_conexion in self.clientes:
                    del self.clientes[id_conexion]
                    print(f"Jugador desconectado: {nombre}")

            cliente_socket.close()

    def procesar_mensaje(self, id_jugador, mensaje):
        """Procesa los mensajes recibidos de los clientes"""
        tipo = mensaje.get('tipo')

        if tipo == 'apuesta':
            cantidad = mensaje.get('cantidad')
            self.manejar_apuesta(id_jugador, cantidad)

        elif tipo == 'pedir':
            self.manejar_pedir_carta(id_jugador)

        elif tipo == 'plantarse':
            self.manejar_plantarse(id_jugador)

        elif tipo == 'nueva_ronda':
            self.manejar_nueva_ronda(id_jugador)

        elif tipo == 'estado':
            self.enviar_estado(id_jugador)

    def manejar_apuesta(self, id_jugador, cantidad):
        """Maneja la apuesta de un jugador"""
        jugador = self.juego.obtener_jugador(id_jugador)
        if jugador and jugador.hacer_apuesta(cantidad):
            print(f"{jugador.nombre} apuestó {cantidad}")

            # Verificar si todos los jugadores han apostado
            self.verificar_apuestas()
        else:
            self.enviar_error(id_jugador, "Apuesta inválida")

    def verificar_apuestas(self):
        """Verifica si todos los jugadores han apostado y comienza a repartir"""
        todos_apostaron = all(
            j.apuesta > 0 for j in self.juego.jugadores.values()
        )

        if todos_apostaron and len(self.juego.jugadores) > 0:
            self.juego.repartir_cartas()
            self.broadcast_estado()

    def manejar_pedir_carta(self, id_jugador):
        """Maneja cuando un jugador pide carta"""
        if self.juego.pedir_carta(id_jugador):
            self.broadcast_estado()
        else:
            jugador = self.juego.obtener_jugador(id_jugador)
            if jugador.mano.esta_busted():
                self.broadcast_estado()

    def manejar_plantarse(self, id_jugador):
        """Maneja cuando un jugador se planta"""
        self.juego.plantarse_jugador(id_jugador)

        # Verificar si todos se han plantado
        self.verificar_fin_ronda()

    def verificar_fin_ronda(self):
        """Verifica si todos los jugadores han terminado su turno"""
        jugadores_activos = [
            j for j in self.juego.jugadores.values()
            if j.estado in ['jugando', 'esperando']
        ]

        if len(jugadores_activos) == 0:
            # Todos han terminado, el crupier juega
            self.juego.jugar_crupier()
            resultados = self.juego.determinar_ganadores()

            # Broadcast de resultados
            for id_conexion, cliente_info in self.clientes.items():
                id_jugador = cliente_info['id_jugador']
                resultado = resultados.get(id_jugador)

                respuesta = {
                    'tipo': 'resultado_ronda',
                    'estado_juego': self.juego.obtener_estado_juego(),
                    'resultado': resultado[0] if resultado else 'error',
                    'ganancia': resultado[1] if resultado else 0
                }

                try:
                    cliente_info['socket'].send(json.dumps(respuesta).encode('utf-8'))
                except:
                    pass

            self.juego.fase = "resultados"
            self.broadcast_estado()

    def manejar_nueva_ronda(self, id_jugador):
        """Maneja cuando se solicita una nueva ronda"""
        # Reiniciar la ronda
        self.juego.iniciar_ronda()
        self.broadcast_estado()

    def broadcast_estado(self):
        """Envía el estado del juego a todos los clientes"""
        estado = self.juego.obtener_estado_juego()
        respuesta = {
            'tipo': 'actualización_estado',
            'estado_juego': estado
        }

        for cliente_info in self.clientes.values():
            try:
                cliente_info['socket'].send(json.dumps(respuesta).encode('utf-8'))
            except:
                pass

    def enviar_error(self, id_jugador, mensaje_error):
        """Envía un mensaje de error a un cliente específico"""
        for cliente_info in self.clientes.values():
            if cliente_info['id_jugador'] == id_jugador:
                respuesta = {
                    'tipo': 'error',
                    'mensaje': mensaje_error
                }
                try:
                    cliente_info['socket'].send(json.dumps(respuesta).encode('utf-8'))
                except:
                    pass
                break

    def enviar_estado(self, id_jugador):
        """Envía el estado del juego a un cliente específico"""
        estado = self.juego.obtener_estado_juego()
        respuesta = {
            'tipo': 'actualización_estado',
            'estado_juego': estado
        }

        for cliente_info in self.clientes.values():
            if cliente_info['id_jugador'] == id_jugador:
                try:
                    cliente_info['socket'].send(json.dumps(respuesta).encode('utf-8'))
                except:
                    pass
                break

    def cerrar(self):
        """Cierra el servidor"""
        self.running = False

        # Cerrar todos los clientes
        for cliente_info in self.clientes.values():
            try:
                cliente_info['socket'].close()
            except:
                pass

        self.servidor.close()
        print("Servidor cerrado.")


if __name__ == '__main__':
    servidor = ServidorBlackjack()
    servidor.iniciar()

