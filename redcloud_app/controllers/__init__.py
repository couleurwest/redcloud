from redcloud_app.controllers.nexclouder import Nextclouder
from redcloud_app.controllers.redminer import Redminer


class Constantine:
    redmine_account: Redminer | None = None
    nextcloud_account: Nextclouder | None = None
    redcloud_status = [
        ('validation', 'In release'),
        ('cours', 'In progress'),
        ('attente', 'In stand by'),
        ('Annulé', 'Closed'),
        ('terminé', 'Closed'),
        ('validé', 'Closed')]

