'''
Created on Jun 13, 2012

@author: vencax
'''
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage
from django.http import HttpResponse


def sendInvoice(invoice, **kwargs):
    ctx = kwargs
    ctx.update({'invoice' : invoice, 'name' : Site.objects.get_current()})
    mailContent = render_to_string('invoices/invoice_mail.html', ctx)
    message = EmailMessage(_('invoice'), mailContent, 
                           invoice.contractor.user.email,
                           [invoice.subscriber.user.email], [])
    
    from pdfgen import InvoicePdfGenerator
    import StringIO
    stream = StringIO.StringIO()
    InvoicePdfGenerator(stream).generate(invoice)
    
    message.attach('%s.pdf' % _('invoice'), stream.getvalue(), 'application/pdf')
    message.send(fail_silently=True)
    
    
def downloadInvoices(invoices, request):
    from pdfgen import InvoicePdfGenerator
    import StringIO
    stream = StringIO.StringIO()
    InvoicePdfGenerator(stream).generate(invoices[0])
    
    return HttpResponse(stream.getvalue(), mimetype='application/pdf')