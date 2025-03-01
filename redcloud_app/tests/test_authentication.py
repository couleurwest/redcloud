import pytest
from redcloud_app.controllers.authentication import Authentication
from redcloud_app.controllers.autorisation import get_otp_code, verify_otp
from redcloud_app.controllers.redminer import Redminer


class UserTemplate:
    """
    Contient les informations de test pour l'authentification Redmine.
    ⚠️ NE JAMAIS METTRE DE DONNÉES SENSIBLES DANS LE CODE !
    """

def test_authentication():
    """
    Teste la création d'un compte sécurisé et la validation OTP.
    """
    assert not Authentication.check_config_file(), "🔴 Le fichier de configuration existe déjà, supprime-le avant de tester."

    # Création du compte et chiffrement des données
    redmine_user = Redminer.signin(
        UserTemplate.redmine_user,
        UserTemplate.redmine_user_password,
        UserTemplate.redmine_key,
        UserTemplate.redmine_url
    )
    assert redmine_user, "🔴 Échec de l'enregistrement du compte Redmine."

    # Génération et validation du code OTP
    otp_code = get_otp_code(redmine_user.otp_secret)
    assert verify_otp(redmine_user.otp_secret, otp_code), "🔴 Erreur d'authentification OTP."

    print("✅ Test de création de compte : OK")


def test_login():
    """
    Teste l'authentification d'un utilisateur avec OTP.
    """
    assert Authentication.check_config_file(), "🔴 Le fichier de configuration n'existe pas. Crée-le avant de tester."

    # Connexion avec les informations stockées
    redmine_user = Redminer.login(UserTemplate.redmine_user, UserTemplate.redmine_user_password)
    assert redmine_user, "🔴 Échec de la connexion à Redmine."

    # Vérification du code OTP généré
    otp_code = get_otp_code(redmine_user.otp_secret)
    assert verify_otp(redmine_user.otp_secret, otp_code), "🔴 Erreur d'authentification OTP."

    print(f"📂 Projets Redmine chargés : {redmine_user.projects}")
    print("✅ Test de connexion : OK")


if __name__ == "__main__":
    pytest.main()
