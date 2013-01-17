'''
Created on May 30, 2012

@author: vencax
'''

from django.dispatch.dispatcher import Signal
from django.utils.translation import ugettext


account_change = Signal(providing_args=[
    'transType', 'vs', 'ss', 'amount', 'destAcc', 'crcAcc', 'currency'
])
"""
This signal is sent when a bank notification mail arrives.
"""

INVOICE_PAY_SYMBOL = 117
DELTA = 0.5


def on_account_change(sender, **kwargs):
    """ account change signal handler.
    Mark appropriate invoice paid.
    """
    amount = kwargs['amount']
    if kwargs['ss'] != INVOICE_PAY_SYMBOL or amount <= 0:
        return

    from .models import Invoice, BadIncommingTransfer
    try:
        invoice = Invoice.objects.get(id=kwargs['vs'])
    except Invoice.DoesNotExist:
        BadIncommingTransfer(invoice=None,
            typee='u', transactionInfo=str(kwargs))

    if invoice.totalPrice() > amount + DELTA:
        BadIncommingTransfer(invoice=invoice, typee='l',
            transactionInfo=str(kwargs)).save()
    elif invoice.totalPrice() < amount - DELTA:
        BadIncommingTransfer(invoice=invoice, typee='m',
            transactionInfo=str(kwargs)).save()
    else:
        invoice.paid = True
        invoice.save()
        _sendPaidNotification(invoice)


def invoice_saved(instance, sender, **kwargs):
    """
    Called on invoice save. It can generate payment request if the invoice
    is incoming. Or notify partner if the invoice is outgoing.
    """
    pass


def _sendPaidNotification(invoice):
    from django.conf import settings
    if getattr(settings, 'INVOICE_PAID_NOTIFICATION', True):
        mailContent = ugettext('Your invoice %(iid)i has been paid' % \
                               {'iid': invoice.id})
        invoice.contractor.user.\
            email_user(ugettext('invoice paid'), mailContent)
