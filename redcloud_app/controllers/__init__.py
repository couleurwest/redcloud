from redcloud_app.controllers.nexclouder import Nextclouder
from redcloud_app.controllers.redminer import Redminer


class Constantine:
    redmine_account: Redminer
    nextcloud_account: Nextclouder
    redcloud_status = [
        ('validation', 'In release'),
        ('cours', 'In progress'),
        ('attente', 'In stand by'),
        ('Annulé', 'Closed'),
        ('terminé', 'Closed'),
        ('validé', 'Closed')]

