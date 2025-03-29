import base64
import json
import os

import yaml
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 200000


class Authentication:
    """
    Classe permettant la gestion de l'authentification sécurisée avec chiffrement AES-256-GCM
    et validation OTP pour Redmine.
    """

    CONFIG_FILE = "assets/.config.enc"

    @classmethod
    def derive_key(cls, password: str, salt: bytes) -> bytes:
        """
        Dérive une clé de chiffrement à partir d'un mot de passe et d'un sel (salt).

        :param password: Mot de passe de l'utilisateur.
        :type password: str
        :param salt: Sel utilisé pour la dérivation de la clé.
        :type salt: bytes
        :return: Clé dérivée de 32 octets.
        :rtype: bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    @classmethod
    def encrypt_data(cls, data: dict, password: str):
        """
        Chiffre les données avec AES-256-GCM et les enregistre dans un fichier.

        :param data: Données à chiffrer (login, clé API Redmine, etc.).
        :type data: dict
        :param password: Mot de passe utilisé pour dériver la clé de chiffrement.
        :type password: str
        """
        salt = os.urandom(16)
        key = cls.derive_key(password, salt)

        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(json.dumps(data).encode()) + encryptor.finalize()

        encrypted_package = [
            base64.b64encode(ciphertext).decode(),
            base64.b64encode(nonce).decode(),
            base64.b64encode(salt).decode(),
            base64.b64encode(encryptor.tag).decode()
        ]

        with open(Authentication.CONFIG_FILE, "w") as f:
            yaml.dump(encrypted_package, f)

    @classmethod
    def decrypt_data(cls, password: str) -> dict:
        """
        Déchiffre les données stockées et retourne leur contenu.

        :param password: Mot de passe pour déchiffrer les données.
        :type password: str
        :raises FileNotFoundError: Si le fichier de configuration n'existe pas.
        :raises ValueError: Si le mot de passe est incorrect ou les données sont corrompues.
        :return: Données déchiffrées sous forme de dictionnaire.
        :rtype: dict
        """
        if not os.path.exists(Authentication.CONFIG_FILE):
            raise FileNotFoundError("Fichier introuvable.")

        with open(Authentication.CONFIG_FILE, "r") as f:
            encrypted_package = yaml.safe_load(f)

        ciphertext = base64.b64decode(encrypted_package[0])
        nonce = base64.b64decode(encrypted_package[1])
        salt = base64.b64decode(encrypted_package[2])
        tag = base64.b64decode(encrypted_package[3])

        key = cls.derive_key(password, salt)

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        try:
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            return json.loads(decrypted_data.decode())
        except Exception:
            raise ValueError("Mot de passe incorrect ou fichier corrompu.")

    @staticmethod
    def check_config_file() -> bool:
        """
        Vérifie si le fichier de configuration chiffré existe.

        :return: True si le fichier existe, False sinon.
        :rtype: bool
        """
        return os.path.exists(Authentication.CONFIG_FILE)

    @classmethod
    def authenticate_user(cls, login: str, password: str) -> dict:
        """
        Authentifie un utilisateur en vérifiant son login et son mot de passe.

        :param login: Identifiant de l'utilisateur.
        :type login: str
        :param password: Mot de passe pour déchiffrer les données.
        :type password: str
        :raises ValueError: Si l'authentification échoue.
        :return: Données de l'utilisateur si l'authentification réussit.
        :rtype: dict
        """
        config = cls.decrypt_data(password)
        if login == config.get("login"):
            return config

        return None

    @classmethod
    def update_config(cls, login, password, **param) -> bool:
        """

        """
        config = cls.decrypt_data(password)
        if login == config.get("login"):
            config.update(**param)
            cls.encrypt_data(config, password)
            return True

        return False
