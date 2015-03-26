from django.db import models
import string, random
from django.db import IntegrityError, transaction
from datetime import date, timedelta

class Mailing(models.Model):
    addr = models.CharField(max_length=255)
    @classmethod
    def daily_fixtures(cls):
        domain_types = ['hotmail.com', 'gmail.com', 'yahoo.com']
        mailings = 100
        batch = []
        print '-- CREATING BATCH OF DAILY MAILING FIXTURES --'
        try:
            with transaction.atomic():
                for mailing in range(mailings):
                    addr = '%s@%s' % (''.join(random.sample(string.ascii_lowercase, 12)), domain_types[random.randint(0, len(domain_types) - 1)])
                    print '-- RANDOM ADDRESS %s' % (addr)
                    batch.append(cls.objects.create(addr=addr))
            print '-- FINISHED CREATED %s MAILINGS' % (len(batch))
        except IntegrityError:
            print '--FAILED TO LOAD FIXTURES--'
        else:
            cls._render_batch(batch)
    @classmethod
    def _render_batch(cls, batch):
        print '-- SAVING BATCH COUNT DATA --'
        domain_map = {}
        for item in batch:
            domain = item.addr.split('@')[1]
            if domain in domain_map:
                domain_map[domain] += 1
            else:
                domain_map[domain] = 1
        print '-- FINISHED BATCH COUNT PROCESSING --'
        MailDomainCounter.save_daily_batch(domain_map)

class MailDomainCounter(models.Model):
    created = models.DateField(auto_now_add=True)
    count = models.PositiveIntegerField()
    domain = models.CharField(max_length=255)
    @classmethod
    def save_daily_batch(cls, data):
        print '--SAVING TO COUNTER TABLE--'
        try:
            with transaction.atomic():
                for k, v in data.iteritems():
                    cls.objects.create(domain=k, count=v)
        except IntegrityError:
            print '--FAILED TO SAVE COUNTERS--'
    @classmethod
    def render_growth_report(cls, days=30, last=50):
        period_map = {}
        total_map = {}
        print '--GATHERING DATA FOR STATISTICAL ANALYSIS--'
        end = date.today()
        start = end - timedelta(days=days)
        print '--I ASSUME I CAN DO A SIMPLE QUERY FOR ALL OBJECTS?--'
        for counter in cls.objects.all():
            d = counter.domain
            c = counter.count
            if (counter.created >= start and counter.created <= end):
                if d in period_map:
                    period_map[d] += c
                else:
                    period_map[d] = c
            if d in total_map:
                total_map[d] += c
            else:
                total_map[d] = c
        print period_map
        domains_count = {}
        print '--RENDERING FINAL REPORT FOR LAST %s' % (days)
        print '--PERCENTAGE GROWTH--'
        for k, v in period_map.iteritems():
            total = total_map.get(k, 0)
            prev = total - v
            domains_count[k] = (((total - prev) / prev) * 100) if prev > 0 else 0
        result = sorted(domains_count.items(), key=lambda x:x[1], reverse=True)[:last]
        print '--FINAL RESULT (%s# of items)--' % (len(result))
        print result
        print '--IF RESULT IS 0, MEANS THERE WAS NO GROWTH, WILL HAPPEN IN THESE TEST RUNS--'
        print '--DO WHATEVER WITH THIS DATA (return etc...)--'
