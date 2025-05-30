# =========================
# CLIENT - Joc Avionașele
# =========================

import socket
import pickle
import threading

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6000
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Ascultare mesaje de la server (notificari + raspunsuri la comenzi)
def listen_to_server():
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            response = pickle.loads(data)
            if 'msg' in response:
                print(f"\n[SERVER]: {response['msg']}")
            elif 'result' in response:
                print(f"\n[REZULTAT]: {response['result']}")
        except:
            break

threading.Thread(target=listen_to_server, daemon=True).start()

# Autentificare cu nume unic
username = input("Introdu numele tau: ")
client_socket.send(pickle.dumps({'cmd': 'login', 'user': username}))

# Loop principal
while True:
    print("\nComenzi: shoot, exit")
    cmd = input(">>> ").strip()

    if cmd == 'exit':
        client_socket.send(pickle.dumps({'cmd': 'exit'}))
        print("[CLIENT] Iesire...")
        break

    elif cmd == 'shoot':
        try:
            lin = int(input("Linie [0-9]: "))
            col = int(input("Coloana [0-9]: "))
            client_socket.send(pickle.dumps({'cmd': 'shoot', 'x': lin, 'y': col}))
        except ValueError:
            print("Valori invalide. Introdu numere de la 0 la 9.")

    else:
        print("Comanda necunoscuta.")

client_socket.close()
