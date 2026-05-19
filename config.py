"""
Archivo de configuración del juego
Puedes modificar estos valores según tus necesidades
"""

# Configuración del servidor
SERVIDOR_HOST = '0.0.0.0'  # Escucha en todas las interfaces
SERVIDOR_PUERTO = 5555      # Puerto de escucha

# Configuración del cliente
CLIENTE_HOST_DEFECTO = 'localhost'  # IP del servidor por defecto
CLIENTE_PUERTO_DEFECTO = 5555       # Puerto del servidor por defecto

# Configuración del juego
DINERO_INICIAL = 1000       # Dinero inicial de cada jugador
NUMERO_MAZOS = 6            # Número de mazos en la baraja

# Tiempos (en segundos)
TIMEOUT_CLIENTE = 30        # Timeout para conexión de cliente
TIEMPO_MAX_TURNO = 300      # Tiempo máximo para el turno de un jugador

# Límites de apuesta
APUESTA_MINIMA = 10
APUESTA_MAXIMA = 1000

# Mensajes
MENSAJE_BIENVENIDA = "¡Bienvenido a Blackjack Multijugador!"
MENSAJE_INICIO_RONDA = "Iniciando nueva ronda..."
MENSAJE_FIN_RONDA = "Ronda finalizada"

