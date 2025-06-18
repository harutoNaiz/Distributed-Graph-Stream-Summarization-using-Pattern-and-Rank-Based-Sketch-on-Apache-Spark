import socket
import pickle
import threading
import time

# Colors
RESET = "\033[0m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"

def receive_results(sock):
    while True:
        try:
            results = pickle.loads(sock.recv(4096))
            print(f"\n{BOLD}{YELLOW}--- Query Results ---{RESET}")
            for res in results:
                src, dest = res['query']
                edge_weight = res['edge_weight']
                reachability = res['reachability']
                print(f"{BOLD}{BLUE}{src} -> {dest}{RESET}")
                print(f"  {GREEN}Edge Weight: {edge_weight}{RESET}")
                print(f"  {YELLOW}Reachable: {reachability}{RESET}")
            print(f"{YELLOW}Waiting for next update...{RESET}")
        except Exception as e:
            print(f"Connection error: {e}")
            break

if __name__ == "__main__":
    config = {
        'width': 1000,
        'depth': 5,
        'pattern_length': 8,
        'conflict_limit': 3,
        'file_path': "/home/pes2ug22cs632/capstoneTeam42/spark_final/dataset/web-NotreDame.txt",
        'queries': [(4, 78), (5, 10)],
        'batch_size': 1000
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 9992))
        s.sendall(pickle.dumps(config))

        print(f"{BOLD}{GREEN}[CLIENT] Connected to Server{RESET}")
        print(f"{YELLOW}Configuration sent successfully{RESET}")

        thread = threading.Thread(target=receive_results, args=(s,), daemon=True)
        thread.start()

        try:
            while thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClient shutting down...")