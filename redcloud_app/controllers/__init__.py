from dreamtools.logmng import CTracker

from redcloud_app.controllers.redminer import Redminer

class Constantine:
    redmine_account: Redminer | None = None
    nextcloud_account = None
    redcloud_status = [
        ('validation', 'In release'),
        ('cours', 'In progress'),
        ('attente', 'In stand by'),
        ('Annulé', 'Closed'),
        ('terminé', 'Closed'),
        ('validé', 'Closed')]
    Jarvis: CTracker | None = None