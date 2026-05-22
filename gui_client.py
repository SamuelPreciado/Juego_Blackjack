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
        self.root.geometry("1100x700")
        self.root.configure(bg="#0b3d0b")

        self.setup_styles()
        self.create_widgets()

    # =========================
    # ESTILOS
    # =========================

    def setup_styles(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Casino.TButton",
            font=("Arial", 14, "bold"),
            padding=10
        )

        style.configure(
            "Title.TLabel",
            background="#0b3d0b",
            foreground="gold",
            font=("Arial", 26, "bold")
        )

    # =========================
    # INTERFAZ
    # =========================

    def create_widgets(self):
        # Ruta de las cartas
        self.cartas_path = os.path.join(os.path.dirname(__file__), "cartas")

        # ======================
        # PANEL CONEXIÓN
        # ======================
        top_frame = tk.Frame(self.root, bg="#1a1a1a")
        top_frame.pack(fill="x", padx=0, pady=0)

        title = tk.Label(
            top_frame,
            text="♠ BLACKJACK MULTIJUGADOR ♠",
            bg="#1a1a1a",
            fg="#FFD700",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=15)

        # Panel de conexión
        conn_frame = tk.Frame(top_frame, bg="#1a1a1a")
        conn_frame.pack()

        tk.Label(conn_frame, text="Servidor:", bg="#1a1a1a", fg="white", font=("Arial", 11)).pack(side="left", padx=8)
        self.host_entry = tk.Entry(conn_frame, font=("Arial", 10), width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side="left", padx=5)

        tk.Label(conn_frame, text="Nombre:", bg="#1a1a1a", fg="white", font=("Arial", 11)).pack(side="left", padx=15)
        self.name_entry = tk.Entry(conn_frame, font=("Arial", 10), width=15)
        self.name_entry.pack(side="left", padx=5)

        self.connect_btn = tk.Button(
            conn_frame,
            text="Conectar",
            bg="#FF6B35",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.connect,
            padx=15,
            pady=5,
            relief="raised",
            bd=2
        )
        self.connect_btn.pack(side="left", padx=10)

        # ======================
        # ÁREA PRINCIPAL DE JUEGO
        # ======================
        game_frame = tk.Frame(self.root, bg="#0b3d0b")
        game_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # --- CRUPIER ---
        dealer_frame = tk.Frame(game_frame, bg="#0b3d0b")
        dealer_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(dealer_frame, text="CRUPIER", bg="#0b3d0b", fg="#FFD700", font=("Arial", 14, "bold")).pack(anchor="w")

        self.dealer_canvas = tk.Canvas(dealer_frame, bg="#0b3d0b", highlightthickness=0, height=200)
        self.dealer_canvas.pack(fill="x", pady=10)

        self.dealer_info = tk.Label(dealer_frame, text="", bg="#0b3d0b", fg="white", font=("Arial", 11))
        self.dealer_info.pack(anchor="w")

        # --- JUGADORES Y RANKING ---
        center_frame = tk.Frame(game_frame, bg="#0b3d0b")
        center_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Ranking a la izquierda
        ranking_frame = tk.Frame(center_frame, bg="#1a1a1a", relief="ridge", bd=2)
        ranking_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(ranking_frame, text="RANKING", bg="#1a1a1a", fg="#FFD700", font=("Arial", 12, "bold")).pack(pady=8)
        self.ranking_text = tk.Text(ranking_frame, height=20, width=25, bg="#2d2d2d", fg="#00FF00", font=("Courier", 10))
        self.ranking_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.ranking_text.config(state="disabled")

        # Jugadores a la derecha
        players_frame = tk.Frame(center_frame, bg="#0b3d0b", relief="ridge", bd=2)
        players_frame.pack(side="left", fill="both", expand=True)

        tk.Label(players_frame, text="JUGADORES", bg="#0b3d0b", fg="#FFD700", font=("Arial", 12, "bold")).pack(pady=8)
        self.players_canvas = tk.Canvas(players_frame, bg="#0b3d0b", highlightthickness=0)
        self.players_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # --- CONTROLES ---
        control_frame = tk.Frame(self.root, bg="#1a1a1a")
        control_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(control_frame, text="Apuesta:", bg="#1a1a1a", fg="white", font=("Arial", 11)).pack(side="left", padx=5)
        self.bet_entry = tk.Entry(control_frame, font=("Arial", 11), width=8)
        self.bet_entry.pack(side="left", padx=5)

        button_configs = [
            ("Apostar", self.make_bet, "#FF6B35"),
            ("Pedir Carta", self.hit, "#4ECDC4"),
            ("Plantarse", self.stand, "#FF6348"),
            ("Nueva Ronda", self.new_round, "#95E1D3")
        ]

        for text, cmd, color in button_configs:
            btn = tk.Button(
                control_frame,
                text=text,
                command=cmd,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                padx=12,
                pady=6,
                relief="raised",
                bd=2
            )
            btn.pack(side="left", padx=5)

        # --- LOG ---
        log_frame = tk.Frame(self.root, bg="#1a1a1a", relief="ridge", bd=2)
        log_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(log_frame, text="EVENTOS", bg="#1a1a1a", fg="#FFD700", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=5)
        self.log_text = tk.Text(log_frame, height=6, bg="#000000", fg="#00FF00", font=("Courier", 9))
        self.log_text.pack(fill="x", padx=5, pady=5)
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

    def update_game(self, estado):

        crupier = estado["crupier"]

        dealer_text = (
            f"{crupier['mano']}\n"
            f"Valor: {crupier['valor']}"
        )

        self.dealer_cards.config(text=dealer_text)

        self.players_text.delete(1.0, tk.END)

        # Mostrar ranking si está presente
        ranking = estado.get("ranking")
        if ranking:
            ranking_lines = "RANKING (por dinero):\n"
            pos = 1
            for item in ranking:
                ranking_lines += f"{pos}. {item['nombre']} - ${item['dinero']}\n"
                pos += 1
            ranking_lines += "\n" + ("="*40) + "\n\n"
            self.players_text.insert(tk.END, ranking_lines)

        for pid, player in estado["jugadores"].items():

            marker = "← TÚ" if int(pid) == self.player_id else ""

            info = (
                f"{player['nombre']} {marker}\n"
                f"Cartas: {player['mano']}\n"
                f"Estado: {player['estado']}\n"
                f"Apuesta: ${player['apuesta']}\n"
                f"Dinero: ${player['dinero']}\n"
                f"{'-'*40}\n"
            )

            self.players_text.insert(tk.END, info)

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