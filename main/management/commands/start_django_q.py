# CharMetrics/main/management/commands/start_django_q.py

from django.core.management.base import BaseCommand
from django_q.cluster import Cluster

class Command(BaseCommand):
    help = 'Starts the Django Q Cluster'

    def handle(self, *args, **kwargs):
        cluster = Cluster()
        cluster.start()
