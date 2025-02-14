import getpass
import os
import yaml
import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from redcloud_app.controllers.autorisation import generate_otp_secret, show_qr_code, verify_otp


ITERATIONS = 200000

class Authentication:

    CONFIG_FILE = "assets/.config.enc"# --- 🔑 Dérivation de clé depuis un mot de passe ---

    @classmethod
    def derive_key(cls,password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    # --- 🔐 Chiffrement AES-256-GCM ---
    @classmethod
    def encrypt_data(cls,data: dict, password: str):
        salt = os.urandom(16)
        key = cls.derive_key(password, salt)

        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(json.dumps(data).encode()) + encryptor.finalize()

        encrypted_package = {
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(encryptor.tag).decode(),
        }

        with open(Authentication.CONFIG_FILE, "w") as f:
            yaml.dump(encrypted_package, f)

    # --- 🔓 Déchiffrement AES-256-GCM ---
    @classmethod
    def decrypt_data(cls,password: str):
        if not os.path.exists(Authentication.CONFIG_FILE):
            raise FileNotFoundError("Fichier introuvable.")

        with open(Authentication.CONFIG_FILE, "r") as f:
            encrypted_package = yaml.safe_load(f)

        salt = base64.b64decode(encrypted_package["salt"])
        nonce = base64.b64decode(encrypted_package["nonce"])
        ciphertext = base64.b64decode(encrypted_package["ciphertext"])
        tag = base64.b64decode(encrypted_package["tag"])

        key = cls.derive_key(password, salt)

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        try:
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            return json.loads(decrypted_data.decode())
        except Exception:
            raise ValueError("Mot de passe incorrect ou fichier corrompu.")

    @staticmethod
    def check_config_file():
        return os.path.exists(Authentication.CONFIG_FILE)

        
    # --- 🔑 Création du compte sécurisé ---
    @classmethod
    def signin(cls, login, password, redmine_key, redmine_url):
        print("⚙️ Création d'un compte sécurisé.")

        otp_secret = generate_otp_secret()

        data = {
            "login": login,
            "redmine_url": redmine_url,
            "redmine_key": redmine_key,
            "otp_secret": otp_secret
        }

        cls.encrypt_data(data, password)
        print("✅ Fichier sécurisé créé avec succès.")
        return otp_secret

    # --- 🔑 Authentification avec OTP ---
    @classmethod
    def authenticate_user(cls, login, password):
        try:
            config = cls.decrypt_data(password)

            return config if login == config.get("login") else None
        
        except Exception as e:
            print("Erreur :", str(e))