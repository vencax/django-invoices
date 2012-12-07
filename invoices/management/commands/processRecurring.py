'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
from django.conf import settings
from django.utils.translation import activate
from django.core.management.base import BaseCommand
from invoices.models import Invoice, RecurringInvoice, Item


class Command(BaseCommand):
    args = ''
    help = 'process recurring invoices'

    def handle(self, freq, *args, **options):
        logging.basicConfig()
        activate(settings.LANGUAGE_CODE)

        freq = int(freq)

        recurrings = RecurringInvoice.objects.filter(frequency__exact=freq)

        for idx, ri in enumerate(recurrings):
            logging.info('Processing ... %i' % idx)
            new = self.process_recurring_invoice(ri.template)
            if ri.autosend:
                new.send()

        logging.info('Done')

    def process_recurring_invoice(self, template):
        new = Invoice(contractor=template.contractor,
                      subscriber=template.subscriber,
                      direction=template.direction,
                      paymentWay=template.paymentWay,
                      currency=template.currency)
        new.save()

        for i in template.items.all():
            newi = Item(name=i.name, count=i.count, price=i.price)
            new.items.add(newi)

        return new
