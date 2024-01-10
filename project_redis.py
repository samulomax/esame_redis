import redis
import hashlib

def redis_client():
    return redis.Redis(
        host='redis-14463.c242.eu-west-1-2.ec2.cloud.redislabs.com',
        port=14463,
        password='tdfA87DGH09gSirZXAEQdelhgluScf4X'
    )

def register_user(username, password):
    client = redis_client()

    if client.hexists('users', username):
        return False

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    client.hset('users', username, hashed_password)
    
    # Inizializza la modalità "Do Not Disturb" a False per il nuovo utente
    client.hset('dnd', username, 'False')
    
    return True

def authenticate_user(username, password):
    client = redis_client()

    if not client.hexists('users', username):
        return False

    stored_password = client.hget('users', username).decode()

    if hashlib.sha256(password.encode()).hexdigest() == stored_password:
        return True

    return False

def get_do_not_disturb_status(username):
    client = redis_client()
    # Ottieni lo stato della modalità "Do Not Disturb" dall'hash 'dnd'
    return client.hget('dnd', username).decode() == 'True'

def set_do_not_disturb(username, status=True):
    client = redis_client()
    
    # Imposta la modalità "Do Not Disturb" nello stato specificato nell'hash 'dnd'
    client.hset('dnd', username, str(status))
    return 'attivata' if status else 'disattivata'

def add_contact(username, contact_username):
    client = redis_client()
    
    if client.hexists('users', username) and client.hexists('users', contact_username):
        client.sadd(f'contacts:{username}', contact_username)
        return True
    
    return False

def login_actions(username):
    while True:
        action = input("Cosa vuoi fare? (aggiungi_contatti/dnd/esci): ").lower()

        if action == 'aggiungi_contatti':
            contact_username = input("Inserisci il nome utente da aggiungere ai contatti: ")
            if add_contact(username, contact_username):
                print(f"{contact_username} aggiunto ai tuoi contatti.")
            else:
                print(f"Impossibile aggiungere {contact_username} ai contatti.")
        elif action == 'dnd':
            new_status = input("Inserisci 'True' per attivare o 'False' per disattivare la modalità 'Do Not Disturb': ").lower()
            if new_status in ['true', 'false']:
                set_do_not_disturb(username, new_status == 'true')
                print(f"Modalità 'Do Not Disturb' {'attivata' if new_status == 'true' else 'disattivata'}.")
            else:
                print("Input non valido. Inserisci 'True' o 'False'.")
        elif action == 'esci':
            break
        else:
            print("Scelta non valida. Scegli tra 'aggiungi_contatti', 'dnd' o 'esci'.")

def main():
    while True:
        choice = input("Cosa vuoi fare? (registrarmi/login/esci): ").lower()

        if choice == 'registrarmi':
            register_new_user()
        elif choice == 'login':
            username = input("Inserisci il nome utente: ")
            password = input("Inserisci la password: ")

            if authenticate_user(username, password):
                print("Login avvenuto con successo")
                login_actions(username)
            else:
                print("Credenziali non valide")
        elif choice == 'esci':
            print("A presto!")
            break
        else:
            print("Scelta non valida. Scegli tra 'registrarmi', 'login' o 'esci'.")

if __name__ == "__main__":
    main()
