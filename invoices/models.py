from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from valueladder.models import Thing

from .signals import invoice_saved
from django.core.mail.message import EmailMessage


class DefaultCurrencySaveMixin(object):
    def save_currency(self):
        if self.currency_id == None:
            self.currency_id = settings.DEFAULT_CURRENCY


class CompanyInfo(models.Model):
    """
    Company info describing business partner.
    """
    user = models.ForeignKey(User, unique=True, related_name='companyinfo')
    bankaccount = models.CharField(_('bankaccount'), max_length=32)
    inum = models.CharField(_('inum'), max_length=32, null=True, blank=True)
    tinum = models.CharField(_('tinum'), max_length=32, null=True, blank=True)
    state = models.CharField(_('state'), max_length=3,
                             default=settings.DEFAULT_STATE_CODE)
    town = models.CharField(_('town'), max_length=32)
    address = models.CharField(_('address'), max_length=64)
    phone = models.IntegerField(_('phone'))
    
    def __unicode__(self):
        return 'Company %s' % self.user.get_full_name()


class Invoice(models.Model, DefaultCurrencySaveMixin):
    """
    Represents an invoice.
    """
    PREPAID = 3
    typeChoices = [
        ('i', _('inInvoice')),
        ('o',  _('outInvoice'))
    ]
    paymentWayChoices = [
        (1,  _('cash')),
        (2,  _('transfer')),
        (PREPAID, _('prepaid')),
    ] 

    issueDate = models.DateField(editable=False, auto_now_add=True)
    contractor = models.ForeignKey(CompanyInfo, verbose_name=_('contractor'),
                                related_name='outinvoices')
    subscriber = models.ForeignKey(CompanyInfo, verbose_name=_('subscriber'),
                                related_name='ininvoices')
    typee = models.CharField(max_length=1, verbose_name=_('typee'),
                             choices=typeChoices)
    paymentWay = models.IntegerField(verbose_name=_('paymentWay'),
                                     choices=paymentWayChoices)
    paid = models.BooleanField(verbose_name=_('paid'),
                               editable=False, default=False)
    currency = models.ForeignKey(Thing, verbose_name=_('currency'))

    @models.permalink
    def get_absolute_url(self):
        return ('invoice_detail', (self.id,))

    def totalPrice(self):
        total = 0
        for i in self.items.all():
            total += (i.price * i.count)
        return total

    def send(self, **kwargs):
        """
        Sends this invoice to partner as mail.
        """
        ctx = kwargs
        ctx.update({'invoice' : self, 'name' : Site.objects.get_current()})
        mailContent = render_to_string('invoices/invoice_mail.html', ctx)
        message = EmailMessage(_('invoice'), mailContent, 
                               self.contractor.user.email,
                               [self.subscriber.user.email], [])
        
        from pdfgen import InvoicePdfGenerator
        import StringIO
        stream = StringIO.StringIO()
        InvoicePdfGenerator(stream).generate(self)
        
        message.attach('%s.pdf' % _('invoice'), stream.getvalue(), 'application/pdf')
        message.send(fail_silently=True)

    def save(self, *args, **kwargs):
        if self.contractor_id == None:
            self.contractor_id = settings.OUR_COMPANY_ID
        self.save_currency()
        super(Invoice, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Do not allow to delete our company ... """
        if self.id != settings.OUR_COMPANY_ID:
            super(Invoice, self).delete(*args, **kwargs)


post_save.connect(invoice_saved, sender=Invoice, dispatch_uid='invoice_save')


class Item(models.Model):
    """
    Represents an invoice item.
    """
    name = models.CharField(max_length=64, verbose_name=_('name'))
    count = models.IntegerField(verbose_name=_('count'), default=1)
    price = models.FloatField(verbose_name=_('price'))
    invoice = models.ForeignKey(Invoice, related_name='items')

    def __unicode__(self):
        return '%s;%s;%s' % (self.name, self.count, self.price)


class BadIncommingTransfer(models.Model):
    """
    This is saved when incoming transfer occurs.
    """
    BITChoices = [
        ('u', _('underPaid')),
        ('o', _('overPaid')),
        ('u', _('unassigned'))
    ]

    invoice = models.ForeignKey(Invoice, null=True, editable=True)
    transactionInfo = models.CharField(max_length=512, verbose_name=_('name'),
                                       editable=True)
    typee = models.CharField(max_length=1, verbose_name=_('typee'),
                             choices=BITChoices, editable=True)

    def __unicode__(self):
        return '%s => %s \n%s' % (self.get_typee_display(), self.invoice,
                                  self.transactionInfo)
