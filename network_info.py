"""
Script para obtener información de red
Útil para determinar la IP del servidor
"""
import socket
import subprocess
import platform
import os


def obtener_ip_local():
    """Obtiene la dirección IP local del computador"""
    try:
        # Crear socket para obtener la IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return None


def obtener_hostname():
    """Obtiene el nombre del computador"""
    try:
        return socket.gethostname()
    except:
        return "unknown"


def obtener_interface_red():
    """Obtiene información de las interfaces de red"""
    sistema = platform.system()

    print("\n" + "=" * 60)
    print("INFORMACIÓN DE RED")
    print("=" * 60)

    print(f"\nSistema Operativo: {sistema}")
    print(f"Hostname: {obtener_hostname()}")

    ip_local = obtener_ip_local()
    if ip_local:
        print(f"IP Local: {ip_local}")

    print("\nInterfaz de Red (IPv4):")

    try:
        if sistema == "Darwin":  # macOS
            resultado = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True
            )
            lineas = resultado.stdout.split('\n')

            interfaz_actual = None
            for linea in lineas:
                if linea and not linea.startswith('\t'):
                    interfaz_actual = linea.split(':')[0]

                if linea.strip().startswith("inet ") and interfaz_actual:
                    ip = linea.strip().split()[1]
                    if not ip.startswith("127"):
                        print(f"  {interfaz_actual}: {ip}")

        elif sistema == "Linux":
            resultado = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True
            )
            ips = resultado.stdout.strip().split()
            for ip in ips:
                print(f"  {ip}")

        elif sistema == "Windows":
            resultado = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True
            )
            lineas = resultado.stdout.split('\n')
            for linea in lineas:
                if "IPv4" in linea or "configuración IP" in linea.lower():
                    print(f"  {linea.strip()}")

    except Exception as e:
        print(f"  Error obteniendo información: {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    obtener_interface_red()

