import redis
import hashlib



# Connessione al database Redis
def redis_client():
    return redis.Redis(
        host='redis-14463.c242.eu-west-1-2.ec2.cloud.redislabs.com:14463',
        port=15124,
        password='tdfA87DGH09gSirZXAEQdelhgluScf4X'
    )

def register_user(username, password):
    # Verifica se l'utente esiste già
    if redis_client.hexists('users', username):
        return False  # Utente già registrato

    # Creazione dell'hash della password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Salvataggio delle credenziali dell'utente nel database
    redis_client.hset('users', username, hashed_password)
    return True  # Registrazione avvenuta con successo

def authenticate_user(username, password):
    # Verifica se l'utente esiste nel database
    if not redis_client.hexists('users', username):
        return False  # Utente non registrato

    # Recupera l'hash della password salvato nel database
    stored_password = redis_client.hget('users', username).decode()

    # Verifica se la password inserita è corretta
    if hashlib.sha256(password.encode()).hexdigest() == stored_password:
        return True  # Autenticazione avvenuta con successo

    return False  # Password errata

# Esempio di utilizzo della registrazione e autenticazione
def main():
    # Registrazione di un nuovo utente
    if register_user('alice', 'password123'):
        print("Registrazione avvenuta con successo")
    else:
        print("Utente già registrato")

    # Autenticazione di un utente
    if authenticate_user('alice', 'password123'):
        print("Login avvenuto con successo")
    else:
        print("Credenziali non valide")

if __name__ == "__main__":
    main()
