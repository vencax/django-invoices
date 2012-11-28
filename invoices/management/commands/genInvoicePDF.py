'''
Created on Dec 29, 2011

@author: vencax
'''
from django.core.management.base import BaseCommand
import logging
from invoices.models import Invoice
from invoices.pdfgen import InvoicePdfGenerator
from django.conf import settings
from django.utils.translation import activate


class Command(BaseCommand):
    args = ''
    help = 'parses incoming mail and\
takes actions base on it'  # @ReservedAssignment

    def handle(self, *args, **options):
        logging.basicConfig()
        activate(settings.LANGUAGE_CODE)

        if len(args) < 2:
            logging.error('USAGE: invoiceID fileToWrite')

        invoiceID = int(args[0])
        logging.info('Generating PDF into %s of invoice %i' %\
                     (args[1], invoiceID))

        invoice = Invoice.objects.get(pk=invoiceID)
        with open(args[1], 'w') as f:
            InvoicePdfGenerator(f).generate(invoice)
