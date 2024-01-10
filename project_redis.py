from datetime import datetime
import redis
import hashlib
import ast 

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

def send_message(username, recipient, message):
    client = redis_client()

    # Verifica se il destinatario è in modalità "Do Not Disturb"
    if get_do_not_disturb_status(recipient):
        print(f"!! IMPOSSIBILE RECAPITARE IL MESSAGGIO, L'UTENTE HA LA MODALITÀ 'Do Not Disturb' ATTIVA")
        return

    # Verifica se il destinatario è nella lista contatti dell'utente
    if client.sismember(f'contacts:{username}', recipient):
        # Crea un ID univoco per il messaggio utilizzando il timestamp corrente
        message_id = datetime.now().timestamp()
        
        # Memorizza i dettagli del messaggio in un hash
        message_details = {
            'sender': username,
            'recipient': recipient,
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        
        # Memorizza il messaggio nella lista delle chat
        client.rpush(f'chat:{username}:{recipient}', str(message_details))
        
        print(f"Messaggio inviato a {recipient}: {message}")
    else:
        print(f"Impossibile inviare il messaggio a {recipient}. L'utente non è nella lista contatti.")

def read_chat(username, other_user):
    client = redis_client()

    # Verifica se l'utente è nella lista contatti
    if not client.sismember(f'contacts:{username}', other_user):
        print(f"L'utente {other_user} non è nella tua lista contatti.")
        return

    # Ottieni tutti i messaggi della chat
    chat_messages = client.lrange(f'chat:{username}:{other_user}', 0, -1)

    print(f">> Chat con {other_user} <<")
    for message_str in chat_messages:
        message_details = ast.literal_eval(message_str.decode())  # Sostituito eval con ast.literal_eval
        prefix = '>' if message_details['sender'] == username else '<'
        print(f"{prefix} {message_details['content']} [{message_details['timestamp']}]")

def login_actions(username):
    while True:
        action = input("Cosa vuoi fare? (aggiungi_contatti/dnd/invia_messaggio/leggi_chat/esci): ").lower()

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
        elif action == 'invia_messaggio':
            recipient = input("Inserisci il nome utente del destinatario: ")
            message = input("Inserisci il messaggio da inviare: ")
            send_message(username, recipient, message)
        elif action == 'leggi_chat':
            other_user = input("Inserisci il nome utente con cui vuoi leggere la chat: ")
            read_chat(username, other_user)
        elif action == 'esci':
            break
        else:
            print("Scelta non valida. Scegli tra 'aggiungi_contatti', 'dnd', 'invia_messaggio', 'leggi_chat', 'esci'.")

def main():
    while True:
        choice = input("Cosa vuoi fare? (registrarmi/login/esci): ").lower()

        if choice == 'registrarmi':
            username = input("Inserisci il tuo nome utente: ")
            password = input("Inserisci la tua password: ")
            if register_user(username, password):
                print("Registrazione avvenuta con successo.")
                login_actions(username)
            else:
                print("Utente già registrato.")
        elif choice == 'login':
            username = input("Inserisci il tuo nome utente: ")
            password = input("Inserisci la tua password: ")
            if authenticate_user(username, password):
                print("Login avvenuto con successo.")
                login_actions(username)
            else:
                print("Credenziali non valide.")
        elif choice == 'esci':
            print("A presto!")
            break
        else:
            print("Scelta non valida. Scegli tra 'registrarmi', 'login', 'esci'.")

if __name__ == "__main__":
    main()
