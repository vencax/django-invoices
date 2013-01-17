'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
from django.conf import settings
from django.utils.translation import activate
from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from valueladder.models import Thing
from invoices.models import CompanyInfo
from invoices.signals import account_change


class Command(BaseCommand):
    help = 'parses incoming account notification mail'  # @ReservedAssignment

    def handle(self, recipient, mailfrom, *args, **options):
        logging.basicConfig()

        data = ' '.join([self.unicodefix(a) for a in args])

        try:
            self.processMail(recipient, mailfrom, data)
        except Exception, e:
            logging.exception(e)

    def unicodefix(self, val):
        try:
            return val.decode('utf-8')
        except UnicodeDecodeError:
            return val
        except UnicodeEncodeError:
            return val

    def processMail(self, recipient, mailfrom, data):
        activate(settings.LANGUAGE_CODE)

        logging.info('Loading %s' % settings.CREDIT_NOTIFICATION_PARSER)

        pMod = __import__(settings.CREDIT_NOTIFICATION_PARSER,
                          globals={}, locals={}, fromlist=['Parser'])
        try:
            parser = pMod.Parser()
            parsed = parser.parse(data)

            logging.info('Parsed: %s' % str(parsed))

            transType, vs, ss, amount, destAcc, crcAcc, currencyCode = parsed
            currency = Thing.objects.get(code=currencyCode)

            account_change.send(sender=CompanyInfo, transType=transType,
                vs=vs, ss=ss, amount=amount, destAcc=destAcc, crcAcc=crcAcc,
                currency=currency)
        except Exception, e:
            logging.exception(e)
            self._onBadVS(data)

    def _onBadVS(self, data):
        mail_admins('Unassotiated payment', data, fail_silently=True)
