from django.core.management.base import NoArgsCommand
from counter.models import *

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        print 'STARTING FIXTURES GENERATION'
        Mailing.daily_fixtures()
        print 'STARTING REPORT'
        MailDomainCounter.render_growth_report()