from io import BytesIO

import pyotp
import qrcode

def generate_otp_secret():
    """
    Génère une clé secrète OTP aléatoire.

    :return: Clé secrète OTP de 32 caractères.
    :rtype: str
    """
    return pyotp.random_base32()

def show_qr_code(secret: str, email: str):
    """
    Génère et affiche un QR Code pour l'ajout de l'OTP dans une application comme Google Authenticator.

    :param secret: Clé secrète OTP.
    :type secret: str
    :param email: Adresse e-mail de l'utilisateur.
    :type email: str
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name="redcloud")
    qr = qrcode.make(uri)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return  buffer

    # qr.show()  Ouvre l’image du QR Code

def verify_otp(secret: str, entered_otp: str) -> bool:
    """
    Vérifie si le code OTP saisi est valide.

    :param secret: Clé secrète OTP.
    :type secret: str
    :param entered_otp: Code OTP saisi par l'utilisateur.
    :type entered_otp: str
    :return: True si le code est valide, False sinon.
    :rtype: bool
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(entered_otp)

def get_otp_code(secret: str) -> str:
    """
    Génère un code OTP basé sur la clé secrète en cours.

    :param secret: Clé secrète OTP.
    :type secret: str
    :return: Code OTP à usage unique.
    :rtype: str
    """
    totp = pyotp.TOTP(secret)
    return totp.now()

