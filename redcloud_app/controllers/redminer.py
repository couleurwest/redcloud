from redminelib import Redmine

# 🔹 Remplace avec l'URL de ton serveur Redmine et ta clé API
REDMINE_URL = "https://redmine.esante-guyane.fr/"
API_KEY = "2de7244c1d584248e1765afb740d4e80c80dd702"  # À récupérer dans ton compte Redmine

# Connexion à Redmine
redmine = Redmine(REDMINE_URL, key=API_KEY)

# Récupérer l'utilisateur courant (celui lié à la clé API)
user = redmine.user.get('current')

# Afficher le login et l'adresse e-mail
print(f"👤 Login: {user.login}")
print(f"📧 Email: {user.mail}")