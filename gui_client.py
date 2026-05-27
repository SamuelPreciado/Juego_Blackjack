import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading
from PIL import Image, ImageTk
import os


class BlackjackGUI:

    def __init__(self):

        self.host = "localhost"
        self.port = 5555

        self.socket = None
        self.connected = False
        self.player_id = None
        self.recv_buffer = ""

        self.root = tk.Tk()
        self.root.title("♠ BLACKJACK MULTIJUGADOR ♠")
        self.root.geometry("1400x900")

        # 🔥 CAMBIO VISUAL: tema claro
        self.root.configure(bg="#f5f6fa")

        self.create_widgets()

    # =========================
    # INTERFAZ
    # =========================

    def create_widgets(self):

        self.cartas_path = os.path.join(os.path.dirname(__file__), "cartas")

        # ======================
        # TOP BAR
        # ======================
        top_frame = tk.Frame(self.root, bg="#ffffff")
        top_frame.pack(fill="x")

        title = tk.Label(
            top_frame,
            text="♠ BLACKJACK MULTIJUGADOR ♠",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=15)

        # ======================
        # CONEXIÓN
        # ======================
        conn_frame = tk.Frame(self.root, bg="#ffffff")
        conn_frame.pack(pady=5)

        tk.Label(conn_frame, text="Servidor:", bg="#ffffff", fg="#2c3e50").pack(side="left", padx=8)

        self.host_entry = tk.Entry(
            conn_frame,
            font=("Arial", 10),
            width=15,
            bg="#ecf0f1",
            relief="flat"
        )
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side="left", padx=5)

        tk.Label(conn_frame, text="Nombre:", bg="#ffffff", fg="#2c3e50").pack(side="left", padx=15)

        self.name_entry = tk.Entry(
            conn_frame,
            font=("Arial", 10),
            width=15,
            bg="#ecf0f1",
            relief="flat"
        )
        self.name_entry.pack(side="left", padx=5)

        self.connect_btn = tk.Button(
            conn_frame,
            text="Conectar",
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=15,
            pady=5,
            command=self.connect
        )
        self.connect_btn.pack(side="left", padx=10)

        # ======================
        # ÁREA PRINCIPAL
        # ======================
        game_frame = tk.Frame(self.root, bg="#f5f6fa")
        game_frame.pack(fill="both", expand=True)

        # --- CRUPIER ---
        dealer_frame = tk.Frame(game_frame, bg="#ffffff")
        dealer_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            dealer_frame,
            text="CRUPIER",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.dealer_canvas = tk.Canvas(
            dealer_frame,
            bg="#ffffff",
            highlightthickness=0,
            height=200
        )
        self.dealer_canvas.pack(fill="x", pady=10)

        self.dealer_info = tk.Label(
            dealer_frame,
            text="",
            bg="#ffffff",
            fg="#2c3e50"
        )
        self.dealer_info.pack(anchor="w")

        # ======================
        # CENTRO
        # ======================
        center_frame = tk.Frame(game_frame, bg="#f5f6fa")
        center_frame.pack(fill="both", expand=True, padx=20)

        # RANKING
        ranking_frame = tk.Frame(center_frame, bg="#ffffff", relief="flat")
        ranking_frame.pack(side="left", fill="y", padx=10)

        tk.Label(
            ranking_frame,
            text="RANKING",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Arial", 12, "bold")
        ).pack(pady=8)

        self.ranking_text = tk.Text(
            ranking_frame,
            height=20,
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Courier", 10),
            relief="flat"
        )
        self.ranking_text.pack()

        # JUGADORES
        players_frame = tk.Frame(center_frame, bg="#ffffff")
        players_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            players_frame,
            text="JUGADORES",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Arial", 12, "bold")
        ).pack(pady=8)

        self.players_canvas = tk.Canvas(
            players_frame,
            bg="#ffffff",
            highlightthickness=0
        )
        self.players_canvas.pack(fill="both", expand=True)

        # ======================
        # CONTROLES
        # ======================
        control_frame = tk.Frame(self.root, bg="#ffffff")
        control_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(control_frame, text="Apuesta:", bg="#ffffff", fg="#2c3e50").pack(side="left")

        self.bet_entry = tk.Entry(
            control_frame,
            width=10,
            bg="#ecf0f1",
            relief="flat"
        )
        self.bet_entry.pack(side="left", padx=5)

        buttons = [
            ("Apostar", self.make_bet, "#27ae60"),
            ("Pedir", self.hit, "#3498db"),
            ("Plantarse", self.stand, "#e67e22"),
            ("Nueva Ronda", self.new_round, "#9b59b6")
        ]

        for text, cmd, color in buttons:
            tk.Button(
                control_frame,
                text=text,
                command=cmd,
                bg=color,
                fg="white",
                relief="flat",
                padx=12,
                pady=5
            ).pack(side="left", padx=5)

        # ======================
        # LOG
        # ======================
        log_frame = tk.Frame(self.root, bg="#ffffff")
        log_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            log_frame,
            text="EVENTOS",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.log_text = tk.Text(
            log_frame,
            height=6,
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Courier", 9),
            relief="flat"
        )
        self.log_text.pack(fill="x")

        self.log_text.config(state="disabled")

    # =========================
    # LOG
    # =========================

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    # =========================
    # CONEXIÓN
    # =========================

    def connect(self):

        host = self.host_entry.get()
        name = self.name_entry.get()

        if not name:
            messagebox.showerror("Error", "Ingresa un nombre")
            return

        try:

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, self.port))

            register = {
                "tipo": "registro",
                "nombre": name
            }

            self.socket.send(json.dumps(register).encode())

            # Leer hasta terminador '\n' para obtener JSON completo
            response = None
            # Intentar recibir datos hasta encontrar '\n'
            while True:
                chunk = self.socket.recv(1024).decode()
                if not chunk:
                    break
                self.recv_buffer += chunk
                if '\n' in self.recv_buffer:
                    line, self.recv_buffer = self.recv_buffer.split('\n', 1)
                    try:
                        response = json.loads(line)
                    except json.JSONDecodeError:
                        response = None
                    break

            self.player_id = response["id_jugador"]

            self.connected = True

            self.log(f"Conectado como {name}")

            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # RECIBIR MENSAJES
    # =========================

    def receive_messages(self):

        while self.connected:

            try:

                data = self.socket.recv(4096).decode()

                if not data:
                    break

                self.recv_buffer += data

                # Procesar todas las líneas completas (cada línea es un JSON)
                while '\n' in self.recv_buffer:
                    linea, self.recv_buffer = self.recv_buffer.split('\n', 1)
                    if not linea.strip():
                        continue
                    try:
                        message = json.loads(linea)
                        self.process_message(message)
                    except json.JSONDecodeError:
                        self.log('Error decodificando JSON recibido')

            except Exception as e:
                self.log(f"Error: {e}")
                break

    # =========================
    # PROCESAR MENSAJES
    # =========================

    def process_message(self, message):

        tipo = message.get("tipo")

        if tipo == "actualización_estado":

            estado = message["estado_juego"]

            self.update_game(estado)

        elif tipo == "resultado_ronda":

            resultado = message["resultado"]
            ganancia = message["ganancia"]

            self.log(f"Resultado: {resultado} | Ganancia: {ganancia}")

            estado = message["estado_juego"]

            self.update_game(estado)

        elif tipo == "error":

            self.log(f"ERROR: {message['mensaje']}")

    # =========================
    # ACTUALIZAR INTERFAZ
    # =========================

    def _load_card_image(self, archivo_carta, width=120, height=180):
        """Carga y redimensiona una imagen de carta desde el archivo."""
        try:
            ruta = os.path.join(self.cartas_path, archivo_carta)
            if not os.path.exists(ruta):
                return None
            img = Image.open(ruta)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def update_game(self, estado):
        # Actualizar cartas del crupier
        self._update_dealer_cards(estado["crupier"])

        # Actualizar ranking
        self._update_ranking(estado.get("ranking", []))

        # Actualizar cartas de jugadores
        self._update_players_cards(estado["jugadores"])

    def _update_dealer_cards(self, crupier):
        """Actualiza la visualización de cartas del crupier."""
        self.dealer_canvas.delete("all")

        # Información del crupier
        valor = crupier.get("valor", 0)
        estado = crupier.get("estado", "esperando")
        info_text = f"Valor: {valor} | Estado: {estado.upper()}"
        self.dealer_info.config(text=info_text)

        # Cargar y mostrar cartas del crupier
        # Extraer cartas de la mano (formato: "2♥, K♠ (Valor: 12)")
        mano_str = crupier.get("mano", "")
        cartas = self._extraer_cartas_de_mano(mano_str)

        x_pos = 20
        for idx, carta_str in enumerate(cartas):
            foto = self._load_card_image(self._get_image_name(carta_str))
            if foto:
                # Guardar referencia para que no sea removida por garbage collection
                if not hasattr(self, 'dealer_photos'):
                    self.dealer_photos = []
                self.dealer_photos.append(foto)
                self.dealer_canvas.create_image(x_pos, 50, image=foto, anchor="nw")
                x_pos += 100

    def _update_ranking(self, ranking):
        """Actualiza la tabla de ranking."""
        self.ranking_text.config(state="normal")
        self.ranking_text.delete(1.0, tk.END)

        if ranking:
            content = ""
            for idx, item in enumerate(ranking, 1):
                nombre = item["nombre"]
                dinero = item["dinero"]
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                content += f"{medal} {nombre:<15}\n     ${dinero:>6}\n\n"
            self.ranking_text.insert(1.0, content)
        else:
            self.ranking_text.insert(1.0, "Esperando jugadores...")

        self.ranking_text.config(state="disabled")

    def _update_players_cards(self, jugadores):
        """Actualiza la visualización de cartas de los jugadores."""
        self.players_canvas.delete("all")

        y_pos = 10
        for pid, player in jugadores.items():
            is_current = int(pid) == self.player_id

            # Nombre del jugador
            nombre_color = "#00FF00" if is_current else "#FFFFFF"
            titulo = f"{'→ ' if is_current else ''}{player['nombre']}"
            self.players_canvas.create_text(10, y_pos, text=titulo, anchor="nw", fill=nombre_color, font=("Arial", 11, "bold"))

            # Estado y dinero
            estado_color = self._get_estado_color(player['estado'])
            info = f"Valor: {player['valor']} | Estado: {player['estado']} | Apuesta: ${player['apuesta']} | Dinero: ${player['dinero']}"
            self.players_canvas.create_text(10, y_pos + 25, text=info, anchor="nw", fill="black", font=("Courier", 9))

            # Cartas del jugador (mostrar miniaturas)
            mano_str = player.get("mano", "")
            cartas = self._extraer_cartas_de_mano(mano_str)

            x_card = 10
            for carta_str in cartas[:5]:  # Máximo 5 cartas visibles
                foto = self._load_card_image(self._get_image_name(carta_str), width=50, height=75)
                if foto:
                    if not hasattr(self, 'player_photos'):
                        self.player_photos = []
                    self.player_photos.append(foto)
                    self.players_canvas.create_image(x_card, y_pos + 50, image=foto, anchor="nw")
                    x_card += 55

            y_pos += 145

        # Ajustar altura del canvas
        self.players_canvas.config(height=max(145 * len(jugadores), 300))

    def _extraer_cartas_de_mano(self, mano_str):
        """Extrae las cartas de la cadena 'A♠, K♥, 5♦ (Valor: XX)'."""
        if not mano_str or "(Valor:" not in mano_str:
            return []
        # Extractar la parte antes de "(Valor:"
        parte_cartas = mano_str.split("(Valor:")[0].strip()
        # Dividir por ", "
        cartas = [c.strip() for c in parte_cartas.split(",")]
        return cartas

    def _get_image_name(self, carta_str):
        """Convierte un string de carta (ej: 'A♠') al nombre del archivo de imagen."""
        if not carta_str:
            return "back.png"

        # Mapeos
        palo_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}
        valor_map = {'A': 'ace', 'J': 'jack', 'Q': 'queen', 'K': 'king'}

        valor = carta_str[0]
        palo_char = carta_str[-1]

        valor_str = valor_map.get(valor, valor)
        palo_str = palo_map.get(palo_char, 'unknown')

        return f"{valor_str}_of_{palo_str}.png"

    def _get_estado_color(self, estado):
        """Retorna el color según el estado del jugador."""
        colores = {
            'jugando': '#FFFF00',
            'plantado': '#00FF00',
            'busted': '#FF0000',
            'ganador': '#00FF00',
            'perdedor': '#FF0000',
            'empate': '#FFFF00',
            'esperando': '#FFFFFF'
        }
        return colores.get(estado, '#FFFFFF')

    # =========================
    # ACCIONES
    # =========================

    def send(self, data):

        if self.connected:
            self.socket.send(
                json.dumps(data).encode()
            )

    def make_bet(self):

        try:

            amount = int(self.bet_entry.get())

            self.send({
                "tipo": "apuesta",
                "cantidad": amount
            })

            self.log(f"Apuesta enviada: {amount}")

        except:
            self.log("Cantidad inválida")

    def hit(self):

        self.send({
            "tipo": "pedir"
        })

    def stand(self):

        self.send({
            "tipo": "plantarse"
        })

    def new_round(self):

        self.send({
            "tipo": "nueva_ronda"
        })

    # =========================
    # EJECUTAR
    # =========================

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    app = BlackjackGUI()
    app.run()