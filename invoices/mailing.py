'''
Created on Jun 13, 2012

@author: vencax
'''
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from django.conf import settings
import StringIO

from .pdfgen import InvoicePdfGenerator


EXTRA_CONTRACTOR_TEXT = getattr(settings, 'EXTRA_CONTRACTOR_TEXT', None)
CUSTOM_FONT = getattr(settings, 'CUSTOM_FONT', 'invoices/OpenSans-Regular.ttf')
invoiceHighlitColor = getattr(settings, 'INVOICE_HIGHLIGHT_COLOR', (0, 0, 1))
fontFile = finders.find(CUSTOM_FONT)
signPicture = finders.find('invoices/invoiceSign.png')
generator = InvoicePdfGenerator(signPicture, fontFile, EXTRA_CONTRACTOR_TEXT,
                                invoiceHighlitColor)


def sendInvoice(invoice, **kwargs):
    ctx = kwargs
    ctx.update({'invoice': invoice, 'name': Site.objects.get_current()})
    mailContent = render_to_string('invoices/invoice_mail.html', ctx)
    message = EmailMessage(_('invoice'), mailContent,
                           invoice.contractor.user.email,
                           [invoice.subscriber.user.email], [])

    stream = StringIO.StringIO()
    generator.generate(invoice, stream)

    message.attach('%s.pdf' % _('invoice'),
                   stream.getvalue(), 'application/pdf')
    message.send(fail_silently=True)


def downloadInvoices(invoices, request):
    if len(invoices) == 1:
        return HttpResponse(_pdfInvoice(invoices[0]),
                            mimetype='application/pdf')
    else:
        return HttpResponse('select only one invoice')


def _pdfInvoice(invoice):
    stream = StringIO.StringIO()
    generator.generate(invoice, stream)
    return stream.getvalue()
