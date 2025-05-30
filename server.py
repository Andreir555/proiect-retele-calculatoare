# =========================
# SERVER - Joc Avionașele
# =========================

import socket
import threading
import pickle
import random
import os
import time

HOST = '127.0.0.1'
PORT = 6000
BUFFER_SIZE = 1024
CONFIG_FOLDER = './config'

clients = {}  # conn: username
client_lock = threading.Lock()

config_list = []
current_config = []
current_heads = set()
heads_hit = set()
game_over = False

def load_configurations():
    global config_list
    for fname in os.listdir(CONFIG_FOLDER):
        with open(os.path.join(CONFIG_FOLDER, fname)) as f:
            matrix = [list(line.strip()) for line in f.readlines() if line.strip()]
            config_list.append(matrix)

def pick_random_config():
    global current_config, current_heads, heads_hit, game_over
    current_config = random.choice(config_list)
    print("Matricea aleasa:", current_config)
    current_heads = set()
    heads_hit = set()
    game_over = False
    for i, row in enumerate(current_config):
        for j, val in enumerate(row):
            if val in 'ABC':
                current_heads.add((i, j))

def notify_all(msg):
    with client_lock:
        for conn in clients:
            try:
                conn.send(pickle.dumps({'msg': msg}))
            except:
                pass

def broadcast_reset():
    notify_all("Jocul a fost resetat. Se incarca o noua configuratie.")
    pick_random_config()

def handle_client(conn, addr):
    global heads_hit, game_over
    username = ''
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            request = pickle.loads(data)
            cmd = request.get('cmd')

            if cmd == 'login':
                username = request['user']
                with client_lock:
                    clients[conn] = username
                print(f"[LOGIN] {username} s-a conectat.")
                conn.send(pickle.dumps({'msg': f'Bun venit, {username}!'}))

            elif cmd == 'shoot':
                if game_over:
                    conn.send(pickle.dumps({'result': '-', 'msg': 'Jocul s-a incheiat. Asteapta urmatoarea runda.'}))
                    continue

                x, y = request['x'], request['y']
                if not (0 <= x < 10 and 0 <= y < 10):
                    conn.send(pickle.dumps({'result': 'Eroare', 'msg': 'Coordonate invalide'}))
                    continue
                cell = current_config[x][y]
                if (x, y) in current_heads:
                    heads_hit.add((x, y))
                    result = 'X'
                elif cell in '123':
                    result = '1'
                else:
                    result = '0'

                response = {'result': result}
                conn.send(pickle.dumps(response))

                if heads_hit == current_heads and not game_over:
                    game_over = True
                    notify_all(f'{username} a doborât toate avioanele!')
                    notify_all("O noua runda va incepe in 3 secunde...")
                    threading.Thread(target=delayed_reset).start()

            elif cmd == 'exit':
                break

    except Exception as e:
        print(f"[EROARE] Client {addr}: {e}")
    finally:
        with client_lock:
            if conn in clients:
                print(f"[DECONECTARE] {clients[conn]} s-a deconectat.")
                del clients[conn]
        conn.close()

def delayed_reset():
    for sec in range(3, 0, -1):
        notify_all(f"Reset in {sec} secunde...")
        time.sleep(1)
    broadcast_reset()

def start_server():
    load_configurations()
    pick_random_config()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] Pornit pe {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()
