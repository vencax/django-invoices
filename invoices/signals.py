'''
Created on May 30, 2012

@author: vencax
'''

from django.dispatch.dispatcher import Signal
from django.utils.translation import ugettext
from django.conf import settings


account_change = Signal(providing_args=['parsed'])
"""
This signal is sent when a bank notification mail arrives.
"""

INVOICE_PAY_SYMBOL = getattr(settings, 'INVOICE_PAY_SYMBOL', 117)
DELTA = 0.5


def on_account_change(sender, parsed, **kwargs):
    """ account change signal handler.
    Mark appropriate invoice paid.
    """
    if not _is_invoice_payment(parsed):
        return

    from .models import Invoice, BadIncommingTransfer
    try:
        invoice = Invoice.objects.get(id=parsed['varSymb'])
    except Invoice.DoesNotExist:
        BadIncommingTransfer(invoice=None,
            typee='u', transactionInfo=str(parsed))

    if invoice.totalPrice() > parsed['amount'] + DELTA:
        BadIncommingTransfer(invoice=invoice, typee='l',
            transactionInfo=str(parsed)).save()
    elif invoice.totalPrice() < parsed['amount'] - DELTA:
        BadIncommingTransfer(invoice=invoice, typee='m',
            transactionInfo=str(parsed)).save()
    else:
        invoice.paid = True
        invoice.save()
        _sendPaidNotification(invoice)
    return 'invoice payment processed'


def invoice_saved(instance, sender, **kwargs):
    """
    Called on invoice save. It can generate payment request if the invoice
    is incoming. Or notify partner if the invoice is outgoing.
    """
    pass


def _sendPaidNotification(invoice):
    if getattr(settings, 'INVOICE_PAID_NOTIFICATION', True):
        mailContent = ugettext('Your invoice %(iid)i has been paid' % \
                               {'iid': invoice.id})
        mailContent += '\n%s\n%f\n' % (invoice.subscriber,
                                       invoice.totalPrice())
        invoice.contractor.user.\
            email_user(ugettext('invoice paid'), mailContent)


def _is_invoice_payment(parsed):
    return parsed['direction'] != 'OUT' and parsed['amount'] > 0 and \
        (parsed['constSymb'] == INVOICE_PAY_SYMBOL or \
         parsed['specSymb'] == INVOICE_PAY_SYMBOL)
