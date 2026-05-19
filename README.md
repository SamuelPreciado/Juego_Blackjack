# 🎰 Blackjack Multijugador Local

Un juego de Blackjack/21 multijugador donde varios jugadores se conectan de forma local a través de red.

## 📋 Requisitos

- Python 3.7 o superior
- Conexión de red local entre los dispositivos

## 🚀 Cómo usar

### 1. Iniciar el Servidor

En el computador que será el servidor:

```bash
python main.py
```

Selecciona la opción **1** para iniciar el servidor. Verás:

```
🎰 Iniciando servidor...
Servidor iniciado en 0.0.0.0:5555
Esperando conexiones de jugadores...
```

**Nota:** La IP 0.0.0.0 significa que escucha en todas las interfaces de red. Los clientes pueden conectarse usando la dirección IP del servidor.

### 2. Obtener la IP del Servidor

En macOS/Linux, obtén la IP local:

```bash
# En macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# En Linux
hostname -I
```

Búsca una dirección como `192.168.x.x` o `10.0.x.x`

### 3. Conectar Clientes

En cada computador de los jugadores:

```bash
python main.py
```

Selecciona la opción **2** para iniciar como cliente. Te pedirá:

- **IP del servidor:** (ejemplo: 192.168.1.100)
- **Puerto:** (por defecto 5555)
- **Tu nombre:** Tu nombre de jugador

## 🎮 Cómo Jugar

### Flujo del Juego

1. **Todos apuestan:** Cada jugador ingresa su apuesta
2. **Se reparten cartas:** El servidor reparte 2 cartas a cada jugador y al crupier
3. **Turno del jugador:** Puedes pedir más cartas o plantarte
4. **Turno del crupier:** Automático (pide cartas hasta 17+)
5. **Resultados:** Se determina el ganador
6. **Nueva ronda:** Comienza de nuevo

### Reglas del Blackjack

- **Objetivo:** Llegar a 21 sin pasarse, o tener más que el crupier
- **Valores de cartas:**
  - Números: Su valor numérico (2-10)
  - Figuras (J, Q, K): 10 puntos
  - As (A): 11 puntos (o 1 si se pasa)
- **Blackjack:** 21 con solo 2 cartas (paga 2:1)
- **Busted:** Si te pasas de 21, pierdes

## 📁 Estructura de Archivos

- `main.py` - Punto de entrada (elegir servidor o cliente)
- `server.py` - Servidor que gestiona la partida
- `client.py` - Cliente para que jueguen los jugadores
- `game.py` - Lógica del juego Blackjack
- `deck.py` - Manejo de la baraja de cartas

## 🎯 Ejemplo de uso en Red Local

**Computador 1 (Servidor):**
```
$ python main.py
1
🎰 Iniciando servidor...
Servidor iniciado en 0.0.0.0:5555
Nueva conexión desde ('192.168.1.101', 54321)
Jugador 'Carlos' registrado (ID: 0)
Jugador 'María' registrado (ID: 1)
```

**Computador 2 (Cliente 1):**
```
$ python main.py
2
IP del servidor: 192.168.1.100
Puerto del servidor: 5555
Tu nombre: Carlos
✓ Bienvenido Carlos
```

**Computador 3 (Cliente 2):**
```
$ python main.py
2
IP del servidor: 192.168.1.100
Puerto del servidor: 5555
Tu nombre: María
✓ Bienvenido María
```

## 🔧 Tecnologías

- **Sockets TCP:** Para comunicación cliente-servidor
- **Threading:** Para manejar múltiples clientes simultáneamente
- **JSON:** Para serialización de mensajes

## 📝 Notas

- El servidor puede manejar múltiples clientes simultáneamente
- Los mensajes se envían en formato JSON
- El crupier juega automáticamente según las reglas
- El dinero de cada jugador se mantiene durante la sesión
- Si un cliente se desconecta, se retira automáticamente del juego

## 🐛 Solución de problemas

**"Conexión rechazada"**
- Verifica que el servidor esté ejecutándose
- Confirma la IP y puerto correctos
- Desactiva el firewall si es necesario

**"Puerto ya en uso"**
- El puerto 5555 podría estar en uso
- Modifica el puerto en server.py si es necesario

**"No se puede conectar a la red"**
- Asegúrate de que todos los dispositivos estén en la misma red local
- Verifica la conexión WiFi o Ethernet

