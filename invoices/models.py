from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CompanyInfo(models.Model):
    """
    Invoice info of an user.
    """
    user = models.ForeignKey(User, unique=True, editable=False)
    bankaccount = models.CharField(_('bankaccount'), max_length=32)
    inum = models.CharField(_('inum'), max_length=32, null=True, blank=True)
    tinum = models.CharField(_('tinum'), max_length=32, null=True, blank=True)


class Invoice(models.Model):
    """
    Represents an invoice.
    """
    typeChoices = [
        ('i', _('inInvoice')),
        ('o',  _('outInvoice'))
    ]

    issueDate = models.DateField(editable=False, auto_now_add=True)
    subscriber = models.ForeignKey(User, related_name='invoices')
    contractor = models.ForeignKey(User, related_name='givenInvoices',
                                   editable=False)
    typee = models.CharField(max_length=1, verbose_name=_('typee'),
                             choices=typeChoices)
    paid = models.BooleanField(verbose_name=_('paid'),
                               editable=False, default=False)
    
    @models.permalink
    def get_absolute_url(self):
        return ('invoice_detail', (self.id,))

    def save(self, *args, **kwargs):
        self.paid = getattr(self, 'paid', None) or False
        self.contractor = getattr(self, 'contractor', None) or \
                          User.objects.get(username='mycompany')
        super(Invoice, self).save(*args, **kwargs)

    def totalPrice(self):
        total = 0
        for i in self.item_set.all():
            total += (i.price * i.count)
        return total

currencyChoices = [
  ('CZK', _('CZKName')),
]

class Item(models.Model):
    """
    Represents an invoice item.
    """
    name = models.CharField(max_length=64, verbose_name=_('name'))
    count = models.IntegerField(verbose_name=_('count'))
    price = models.FloatField(verbose_name=_('price'))
    invoice = models.ForeignKey(Invoice)
    currency = models.CharField(max_length=3, verbose_name=_('currency'),
                                choices=currencyChoices,
                                default=settings.DEFAULT_CURRENCY)

    def __unicode__(self):
        return self.name

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