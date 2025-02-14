import pyotp
import qrcode


# --- 📲 Génération de la clé OTP ---
def generate_otp_secret():
    return pyotp.random_base32()

# --- 📷 Affichage du QR Code pour Google Authenticator ---
def show_qr_code(secret, email):
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name="redcloud")
    qr = qrcode.make(uri)
    qr.show()  # Ouvre l’image du QR Code

# --- 🔑 Vérification OTP ---
def verify_otp(secret, entered_otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(entered_otp)

