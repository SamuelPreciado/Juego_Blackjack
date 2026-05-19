"""
Punto de entrada principal para el juego Blackjack multijugador
Permite elegir entre ejecutar el servidor o el cliente
"""
import subprocess
import sys
import os


def main():
    """Menú principal"""
    print("\n" + "=" * 60)
    print("BLACKJACK MULTIJUGADOR")
    print("=" * 60)
    print("\n¿Qué deseas hacer?")
    print("\n1. Iniciar SERVIDOR (esperar conexiones de jugadores)")
    print("2. Conectar como CLIENTE (unirse a una partida)")
    print("3. Salir")

    opcion = input("\nSelecciona una opción (1-3): ").strip()

    if opcion == '1':
        print("\n🎰 Iniciando servidor...")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'server.py')])

    elif opcion == '2':
        print("\n🎲 Iniciando cliente...")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'client.py')])

    elif opcion == '3':
        print("Saliendo...")
        sys.exit(0)

    else:
        print("Opción inválida")


if __name__ == '__main__':
    main()
