"""
Tests pour la connexion à Redmine et la récupération des informations utilisateur.

Ce module effectue les tests suivants :
✅ Vérification de la connexion à Redmine
✅ Vérification que l'utilisateur connecté possède un login et une adresse e-mail
✅ Vérification de la récupération des tickets assignés à l'utilisateur
✅ Test de création d'une entrée de temps sur un ticket
"""

import datetime
import pytest
from redminelib import Redmine
from redminelib.exceptions import AuthError, ResourceNotFoundError

# 🔹 Remplace avec l'URL de ton serveur Redmine et une clé API valide
REDMINE_URL = "https://redmine.esante-guyane.fr"
API_KEY = "2de7244c1d584248e1765afb740d4e80c80dd702"

class RdUser:
    """Classe contenant les informations de l'utilisateur Redmine."""
    pseudo = ""
    email = ""
    user_id = None
    projects = {}
    issues = {}

@pytest.fixture(scope="module")
def redmine_client():
    """
    Fixture pour établir la connexion à Redmine.

    :return: Instance Redmine connectée avec la clé API.
    :rtype: redminelib.Redmine
    """
    try:
        client = Redmine(REDMINE_URL, key=API_KEY, requests={"verify": False})
        user = client.user.get('current')

        RdUser.pseudo = user.login
        RdUser.email = user.mail
        RdUser.user_id = user.id

        print(f"✅ Connexion réussie : {user.login} ({user.id})")

        return client
    except AuthError:
        pytest.exit("❌ Échec de l'authentification : clé API invalide", returncode=1)
    except ResourceNotFoundError:
        pytest.exit("❌ Impossible de récupérer les informations de l'utilisateur", returncode=1)

def test_redmine_userinfo():
    """
    Vérifie que les informations de l'utilisateur connecté sont bien récupérées.
    """
    assert RdUser.pseudo, "L'utilisateur doit avoir un pseudo"
    assert RdUser.email, "L'utilisateur doit avoir une adresse e-mail"
    assert RdUser.user_id, "L'utilisateur doit avoir un identifiant"

def test_redmine_user_issues(redmine_client):
    """
    Vérifie que l'utilisateur connecté possède des tickets ouverts et récupère leurs informations.

    - Récupère la liste des tickets assignés à l'utilisateur.
    - Vérifie que des tickets existent.
    - Stocke les informations des tickets et des projets associés dans `RdUser.issues` et `RdUser.projects`.
    """
    issues = redmine_client.issue.filter(
        assigned_to_id=RdUser.user_id,
        sort='project_id:asc;due_date:desc',
        status_id='open'
    )

    assert issues, "L'utilisateur n'a pas de demande assignée"

    for issue in issues:
        project = issue.project
        if project.id not in RdUser.projects:
            RdUser.projects[project.id] = {
                'name': project.name,
                'categories': [(cat.id, cat.name) for cat in project.issue_categories],
                'trackers': [(cat.id, cat.name) for cat in project.trackers],
                'time_entry_activities': [(cat.id, cat.name) for cat in project.time_entry_activities]
            }

        RdUser.issues[issue.id] = {
            'subject': issue.subject,
            'priority': issue.priority.name,
            'tracker': (issue.tracker.id, issue.tracker.name),
            'category': (issue.category.id, issue.category.name) if hasattr(issue, "category") else (),
            'description': issue.description,
            'due_date': issue.due_date,
        }

    print(f"✅ {len(RdUser.issues)} tickets récupérés")

def test_redmine_time_entry(redmine_client):
    """
    Vérifie la création d'une entrée de temps sur un ticket spécifique.

    - Crée une entrée de temps sur le ticket ID 1077.
    - Vérifie que l'entrée de temps a bien été enregistrée.
    """
    time_entry = redmine_client.time_entry.create(
        issue_id=1077,
        spent_on=datetime.date.today(),
        hours=0.1,
        activity_id=28,
        user_id=RdUser.user_id,
        comments='open'
    )

    assert time_entry, "L'entrée de temps n'a pas été enregistrée"
    print("✅ Enregistrement de temps réussi")
