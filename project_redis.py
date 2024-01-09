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
    return True

def authenticate_user(username, password):
    client = redis_client()

    if not client.hexists('users', username):
        return False

    stored_password = client.hget('users', username).decode()

    if hashlib.sha256(password.encode()).hexdigest() == stored_password:
        return True

    return False

def search_users(query):
    client = redis_client()
    all_users = client.hkeys('users')
    matching_users = [user.decode() for user in all_users if query.lower() in user.decode().lower()]
    return matching_users

def add_contact(username, contact_username):
    client = redis_client()
    
    # Verifica se l'utente e il contatto esistono
    if client.hexists('users', username) and client.hexists('users', contact_username):
        # Aggiungi il contatto alla lista del'utente
        client.sadd(f'contacts:{username}', contact_username)
        return True
    
    return False

def set_do_not_disturb(username, status=True):
    client = redis_client()
    
    # Imposta la modalità "Do Not Disturb"
    client.set(f'dnd:{username}', int(status))
    return True

def main():
    # Esegui l'autenticazione (puoi sostituire con i tuoi dati di accesso)
    if authenticate_user('alice', 'password123'):
        print("Login avvenuto con successo")
        
        # Esempio di ricerca utenti
        search_query = 'a'
        results = search_users(search_query)
        
        if results:
            print(f"Utenti che corrispondono a '{search_query}': {results}")
        else:
            print(f"Nessun utente trovato per '{search_query}'")

        # Esempio di aggiunta di un contatto
        if add_contact('alice', 'bob'):
            print("Contatto aggiunto con successo")
        else:
            print("Impossibile aggiungere il contatto")

        # Esempio di impostazione della modalità "Do Not Disturb"
        if set_do_not_disturb('alice', True):
            print("Modalità 'Do Not Disturb' attivata")
        else:
            print("Impossibile attivare la modalità 'Do Not Disturb'")

    else:
        print("Credenziali non valide")

if __name__ == "__main__":
    main()
