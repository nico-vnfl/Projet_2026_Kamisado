from inscription import start_server, subscribe
import time

# Lancement
if __name__ == "__main__":

    start_server()
    subscribe()

    # Boucle pour garder le serveur local actif
    while True:
        time.sleep(1)
