'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
from django.conf import settings
from django.utils.translation import activate
from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from invoices.models import CompanyInfo, BadIncommingTransfer
from invoices.signals import account_change


class Command(BaseCommand):
    help = 'parses incoming account notification mail'  # @ReservedAssignment

    def handle(self, recipient, mailfrom, *args, **options):
        if options.get('v', 1) == 3:
            logging.basicConfig(filename=None, level=logging.DEBUG)
        else:
            logging.basicConfig(filename=None, level=logging.WARN)

        activate(settings.LANGUAGE_CODE)

        data = ' '.join([self.unicodefix(a) for a in args])

        try:
            self.processMail(recipient, mailfrom, data)
        except Exception:
            import traceback
            self._onBadVS(data, traceback.format_exc())

    def unicodefix(self, val):
        try:
            return val.decode('utf-8')
        except UnicodeDecodeError:
            return val
        except UnicodeEncodeError:
            return val

    def processMail(self, recipient, mailfrom, data):
        logging.info('Loading %s' % settings.CREDIT_NOTIFICATION_PARSER)

        pMod = __import__(settings.CREDIT_NOTIFICATION_PARSER,
                          globals={}, locals={}, fromlist=['Parser'])

        parser = pMod.Parser()
        parsed = parser.parse(data)

        logging.info('Parsed: %s' % str(parsed))
        results = account_change.send(sender=CompanyInfo, parsed=parsed)
        logging.debug('Parsed: %s' % str(results))
        for _, res in results:
            if res:
                return
        # here we have no account_change handler called
        BadIncommingTransfer(typee='u', transactionInfo=str(parsed)).save()

    def _onBadVS(self, data, excp):
        mail_admins('account notification error', '%s\n%s' % (data, excp),
                    fail_silently=True)
