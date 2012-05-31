from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save

from .signals import invoice_saved, user_saved
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

class CompanyInfo(models.Model):
    """
    Invoice info of an user.
    """
    user = models.ForeignKey(User, unique=True, editable=False,
                             related_name='companyinfo')
    bankaccount = models.CharField(_('bankaccount'), max_length=32)
    inum = models.CharField(_('inum'), max_length=32, null=True, blank=True)
    tinum = models.CharField(_('tinum'), max_length=32, null=True, blank=True)
    state = models.CharField(_('state'), max_length=3, 
                             default=settings.DEFAULT_STATE_CODE)
    town = models.CharField(_('town'), max_length=32)
    address = models.CharField(_('address'), max_length=64)
    phone = models.IntegerField(_('phone'))
    
post_save.connect(user_saved, sender=User, dispatch_uid='user_saves')


class Invoice(models.Model):
    """
    Represents an invoice.
    """
    typeChoices = [
        ('i', _('inInvoice')),
        ('o',  _('outInvoice'))
    ]

    issueDate = models.DateField(editable=False, auto_now_add=True)
    partner = models.ForeignKey(User, verbose_name=_('partner'),
                                related_name='invoices')
    typee = models.CharField(max_length=1, verbose_name=_('typee'),
                             choices=typeChoices)
    paid = models.BooleanField(verbose_name=_('paid'),
                               editable=False, default=False)
    
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
        self.partner.email_user(self, mailContent)
    
post_save.connect(invoice_saved, sender=Invoice, dispatch_uid='invoice_save')


currencyChoices = [
  ('CZK', _('CZKName')),
]

class Item(models.Model):
    """
    Represents an invoice item.
    """
    name = models.CharField(max_length=64, verbose_name=_('name'))
    count = models.IntegerField(verbose_name=_('count'), default=1)
    price = models.FloatField(verbose_name=_('price'))
    invoice = models.ForeignKey(Invoice, related_name='items')
    currency = models.CharField(max_length=3, verbose_name=_('currency'),
                                choices=currencyChoices,
                                default=settings.DEFAULT_CURRENCY)

    def __unicode__(self):
        return '%s;%s;%s;%s' % (self.name, self.count, 
                                self.price, self.currency)

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