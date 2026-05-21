import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading


class BlackjackGUI:

    def __init__(self):

        self.host = "localhost"
        self.port = 5555

        self.socket = None
        self.connected = False
        self.player_id = None

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

        title = ttk.Label(
            self.root,
            text="BLACKJACK ONLINE",
            style="Title.TLabel"
        )

        title.pack(pady=10)

        # ======================
        # PANEL SUPERIOR
        # ======================

        top_frame = tk.Frame(self.root, bg="#0b3d0b")
        top_frame.pack(fill="x", padx=20)

        tk.Label(
            top_frame,
            text="Servidor:",
            bg="#0b3d0b",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left")

        self.host_entry = tk.Entry(top_frame)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side="left", padx=5)

        tk.Label(
            top_frame,
            text="Nombre:",
            bg="#0b3d0b",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=10)

        self.name_entry = tk.Entry(top_frame)
        self.name_entry.pack(side="left")

        self.connect_btn = ttk.Button(
            top_frame,
            text="Conectar",
            style="Casino.TButton",
            command=self.connect
        )

        self.connect_btn.pack(side="left", padx=10)

        # ======================
        # CRUPIER
        # ======================

        dealer_frame = tk.LabelFrame(
            self.root,
            text="CRUPIER",
            bg="#145214",
            fg="white",
            font=("Arial", 16, "bold"),
            padx=10,
            pady=10
        )

        dealer_frame.pack(fill="x", padx=20, pady=10)

        self.dealer_cards = tk.Label(
            dealer_frame,
            text="",
            bg="#145214",
            fg="white",
            font=("Arial", 18)
        )

        self.dealer_cards.pack()

        # ======================
        # JUGADORES
        # ======================

        players_frame = tk.LabelFrame(
            self.root,
            text="JUGADORES",
            bg="#145214",
            fg="white",
            font=("Arial", 16, "bold"),
            padx=10,
            pady=10
        )

        players_frame.pack(fill="both", expand=True, padx=20)

        self.players_text = tk.Text(
            players_frame,
            height=15,
            bg="#1e1e1e",
            fg="white",
            font=("Consolas", 13)
        )

        self.players_text.pack(fill="both", expand=True)

        # ======================
        # CONTROLES
        # ======================

        controls = tk.Frame(self.root, bg="#0b3d0b")
        controls.pack(pady=10)

        self.bet_entry = tk.Entry(controls, width=10, font=("Arial", 14))
        self.bet_entry.pack(side="left", padx=5)

        self.bet_btn = ttk.Button(
            controls,
            text="Apostar",
            style="Casino.TButton",
            command=self.make_bet
        )

        self.bet_btn.pack(side="left", padx=5)

        self.hit_btn = ttk.Button(
            controls,
            text="Pedir Carta",
            style="Casino.TButton",
            command=self.hit
        )

        self.hit_btn.pack(side="left", padx=5)

        self.stand_btn = ttk.Button(
            controls,
            text="Plantarse",
            style="Casino.TButton",
            command=self.stand
        )

        self.stand_btn.pack(side="left", padx=5)

        self.new_round_btn = ttk.Button(
            controls,
            text="Nueva Ronda",
            style="Casino.TButton",
            command=self.new_round
        )

        self.new_round_btn.pack(side="left", padx=5)

        # ======================
        # LOG
        # ======================

        log_frame = tk.LabelFrame(
            self.root,
            text="EVENTOS",
            bg="#145214",
            fg="white",
            font=("Arial", 14, "bold")
        )

        log_frame.pack(fill="x", padx=20, pady=10)

        self.log_text = tk.Text(
            log_frame,
            height=8,
            bg="black",
            fg="#00ff00",
            font=("Consolas", 11)
        )

        self.log_text.pack(fill="x")

    # =========================
    # LOG
    # =========================

    def log(self, message):

        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

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

            response = json.loads(
                self.socket.recv(1024).decode()
            )

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

                message = json.loads(data)

                self.process_message(message)

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