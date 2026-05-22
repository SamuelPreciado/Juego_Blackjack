# 🎰 Blackjack Multijugador Local

Un juego de Blackjack/21 multijugador donde varios jugadores se conectan de forma local a través de red. Incluye interfaz gráfica mejorada con imágenes de cartas y sistema de ranking en tiempo real.

## 📋 Requisitos

- Python 3.7 o superior
- Pillow (para visualización de imágenes de cartas)
- Conexión de red local entre los dispositivos

## 🚀 Instalación de Dependencias

```bash
pip3 install -r requirements.txt
```

## 🎮 Interfaces Disponibles

### Opción 1: Interfaz Gráfica (Recomendada)
```bash
python3 gui_client.py
```
- Interfaz visual moderna
- Cartas mostradas como imágenes
- Tabla de ranking en tiempo real
- Indicadores de estado por colores

### Opción 2: Cliente de Consola
```bash
python3 client.py
```
- Interfaz de texto
- Ideal para sistemas sin GUI

### Opción 3: Menú Principal
```bash
python3 main.py
```
- Permite elegir entre servidor o cliente
- Cliente CLI por defecto

## 📋 Cómo usar

### 1. Iniciar el Servidor

En el computador que será el servidor:

```bash
python3 server.py
```

Verás:

```
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

#### Con Interfaz Gráfica:
```bash
python3 gui_client.py
```
- Ingresa la IP del servidor
- Ingresa tu nombre de jugador
- Haz click en "Conectar"

#### Con Cliente de Consola:
```bash
python3 client.py
```
Te pedirá:
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

## 🎨 Características de la Interfaz Gráfica

### Visualización de Cartas
- Les cartas se muestran como **imágenes reales** de una baraja estándar
- Las cartas se redimensionan automáticamente para mejor visibilidad
- Soporte para todas las 52 cartas (A-K en 4 palos)
- Reversibles del mazo mostradas nítidamente

### Tabla de Ranking
- Muestra los jugadores ordenados por cantidad de dinero (descendente)
- Se actualiza automáticamente después de cada ronda
- Indicadores visuales: 🥇 🥈 🥉
- Visualización en tiempo real del dinero de cada jugador

### Indicadores de Estado
- Colores según el estado del jugador:
  - 🟡 Jugando (amarillo)
  - 🟢 Plantado (verde)
  - 🔴 Busted (rojo)
  - 🟢 Ganador (verde)
  - 🔴 Perdedor (rojo)

### Controles Intuitivos
- Botones claramente etiquetados
- Campo para ingreso de apuestas
- Log de eventos en tiempo real
- Indicador de estado de conexión

## 📁 Estructura de Archivos

- `main.py` - Punto de entrada (elegir servidor o cliente)
- `server.py` - Servidor que gestiona la partida
- `client.py` - Cliente CLI para jugadores
- `gui_client.py` - Cliente GUI con cartas e imágenes
- `game.py` - Lógica del juego Blackjack
- `deck.py` - Manejo de la baraja de cartas
- `cartas/` - Carpeta con imágenes de todas las cartas
- `requirements.txt` - Dependencias de Python

## 🔧 Tecnologías

- **Sockets TCP:** Para comunicación cliente-servidor
- **Threading:** Para manejar múltiples clientes simultáneamente
- **JSON:** Para serialización de mensajes
- **Tkinter:** Para interfaz gráfica
- **Pillow:** Para procesamiento de imágenes de cartas

## ✨ Mejoras Recientes

### Versión 2.0
- ✅ Interfaz gráfica mejorada con tema moderno
- ✅ Visualización de cartas como imágenes
- ✅ Sistema de ranking en tiempo real
- ✅ Indicadores de estado coloreados
- ✅ Mejor disposición de widgets
- ✅ Log de eventos mejorado
- ✅ Soporte para múltiples jugadores

### Versión 1.0
- ✅ Servidor multijugador funcional
- ✅ Cliente CLI
- ✅ Reglas de Blackjack
- ✅ Sistema de apuestas

## 📝 Notas

- El servidor puede manejar múltiples clientes simultáneamente
- Los mensajes se envían en formato JSON con delimitador `\n` para evitar conflictos
- El crupier juega automáticamente según las reglas
- El dinero de cada jugador se mantiene durante la sesión
- Si un cliente se desconecta, se retira automáticamente del juego
- Las imágenes de cartas se cargan desde la carpeta `cartas/`

## 🐛 Solución de problemas

**"Conexión rechazada"**
- Verifica que el servidor esté ejecutándose
- Confirma la IP y puerto correctos
- Desactiva el firewall si es necesario

**"No se importa Pillow"**
- Ejecuta: `pip3 install Pillow`

**"Puerto ya en uso"**
- El puerto 5555 podría estar en uso
- Modifica el puerto en server.py si es necesario

**"No se pueden cargar las imágenes de cartas"**
- Verifica que la carpeta `cartas/` existe en el mismo directorio
- Las imágenes deben tener nombres como `ace_of_spades.png`

**"No se puede conectar a la red"**
- Asegúrate de que todos los dispositivos estén en la misma red local
- Verifica la conexión WiFi o Ethernet
