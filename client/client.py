import socket
import pickle
import threading
import time

RESET = "\033[0m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"

def receive_results(sock):
    while True:
        try:
            results = pickle.loads(sock.recv(4096))
            print(f"\n{BOLD}{YELLOW}--- Adaptive Hash Sketch Results ---{RESET}")
            
            for res in results:
                if res.get('type') == 'stats':
                    stats = res['stats']
                    print(f"{BOLD}{CYAN}=== Sketch Statistics ==={RESET}")
                    print(f"  {MAGENTA}Hash Functions: {stats['hash_functions']}{RESET}")
                    print(f"  {MAGENTA}Total Edges: {stats['total_edges']}{RESET}")
                    print(f"  {MAGENTA}Total Weight: {stats['total_weight']:.2f}{RESET}")
                    print(f"  {MAGENTA}Occupied Cells: {stats['occupied_cells']}/{stats['total_cells']}{RESET}")
                    print(f"  {MAGENTA}Occupancy Rate: {stats['occupancy_rate']:.2%}{RESET}")
                else:
                    src, dest = res['query']
                    edge_weight = res['edge_weight']
                    reachability = res['reachability']
                    print(f"{BOLD}{BLUE}{src} -> {dest}{RESET}")
                    print(f"  {GREEN}Edge Weight: {edge_weight:.2f}{RESET}")
                    print(f"  {YELLOW}Reachable: {reachability}{RESET}")
            
            print(f"{CYAN}Waiting for next update...{RESET}")
        except Exception as e:
            print(f"{RED}Connection error: {e}{RESET}")
            break

if __name__ == "__main__":
    config = {
        'width': 1000,
        'depth': 5,
        'pattern_length': 8,
        'conflict_limit': 3,
        'file_path': "../dataset/web-NotreDame.txt", 
        'queries': [(4, 78), (5, 10)],
        'batch_size': 1000
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 9992))
        s.sendall(pickle.dumps(config))

        print(f"{BOLD}{GREEN}[CLIENT] Connected to Adaptive Hash Sketch Server{RESET}")
        print(f"{YELLOW}Configuration sent successfully{RESET}")
        print(f"{CYAN}Starting adaptive collision handling...{RESET}")

        thread = threading.Thread(target=receive_results, args=(s,), daemon=True)
        thread.start()

        try:
            while thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{RED}Client shutting down...{RESET}")
