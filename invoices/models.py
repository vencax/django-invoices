from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from valueladder.models import Thing

from .signals import invoice_saved
from .mailing import sendInvoice
import datetime

INVOICE_DUE_INTERVAL = getattr(settings, 'INVOICE_DUE_INTERVAL', 14)

class CompanyInfoObjectManager(models.Manager):
    """ Object manager that offers get_default thing method """
    def get_our_company_info(self):
        return self.get(user__id=settings.OUR_COMPANY_ID)

class CompanyInfo(models.Model):
    """
    Company info describing business partner.
    """
    class Meta:
        verbose_name = _('company info')
        verbose_name_plural = _('company infos')
        ordering = ['user__last_name']
    
    objects = CompanyInfoObjectManager()
    
    user = models.ForeignKey(User, verbose_name=_('user'), unique=True, 
                             related_name='companyinfo')
    bankaccount = models.CharField(_('bankaccount'), max_length=32,
                                   default='------')
    inum = models.CharField(_('inum'), max_length=32, null=True, blank=True)
    tinum = models.CharField(_('tinum'), max_length=32, null=True, blank=True)
    state = models.CharField(_('state'), max_length=3,
                             default=settings.DEFAULT_STATE_CODE)
    town = models.CharField(_('town'), max_length=32)
    zipcode = models.CharField(_('zipcode'), max_length=32,
                               default='------')
    address = models.CharField(_('address'), max_length=64, default='------')
    phone = models.IntegerField(_('phone'), default=0)
    
    def __unicode__(self):
        return self.user.get_full_name()
    
    def delete(self, *args, **kwargs):
        """ Do not allow to delete our company ... """
        if self.user__id != settings.OUR_COMPANY_ID:
            super(Invoice, self).delete(*args, **kwargs)


class Invoice(models.Model):
    """
    Represents an invoice.
    """
    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        ordering = ['issueDate']
    
    dirChoices = [
        ('i', _('inInvoice')),
        ('o',  _('outInvoice'))
    ]
    paymentWayChoices = [
        (1,  _('cash')),
        (2,  _('transfer')),
    ]

    issueDate = models.DateField(verbose_name=_('issueDate'), editable=False, 
                                 auto_now_add=True)
    contractor = models.ForeignKey(CompanyInfo, verbose_name=_('contractor'),
                                related_name='outinvoices')
    subscriber = models.ForeignKey(CompanyInfo, verbose_name=_('subscriber'),
                                related_name='ininvoices')
    direction = models.CharField(max_length=1, verbose_name=_('direction'),
                                 choices=dirChoices, default='o')
    paymentWay = models.IntegerField(verbose_name=_('paymentWay'),
                                     choices=paymentWayChoices, default=2)
    paid = models.BooleanField(verbose_name=_('paid'),
                               editable=False, default=False)
    currency = models.ForeignKey(Thing, verbose_name=_('currency'))
    
    def __unicode__(self):
        return '%s %i' % (_('invoice'), self.id)
    
    @property
    def dueDate(self):
        return self.issueDate + datetime.timedelta(INVOICE_DUE_INTERVAL)

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
        sendInvoice(self, **(kwargs))

    def save(self, *args, **kwargs):
        if self.contractor_id == None:
            self.contractor = self.get_my_company_info()
        if self.currency_id == None:
            self.currency = self.get_default_currency()
        super(Invoice, self).save(*args, **kwargs)


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
    class Meta:
        verbose_name = _('bad incomming transfer')
        verbose_name_plural = _('bad incomming transfers')
        ordering = ['invoice__issueDate']
    
    BITChoices = [
        ('u', _('underPaid')),
        ('o', _('overPaid')),
        ('u', _('unassigned'))
    ]

    invoice = models.ForeignKey(Invoice, null=True, editable=True)
    transactionInfo = models.TextField(max_length=512, editable=True,
                                       verbose_name=_('transaction info'))
    typee = models.CharField(max_length=1, verbose_name=_('reason'),
                             choices=BITChoices, editable=True)

    def __unicode__(self):
        return '%s => %s \n%s' % (self.get_typee_display(), self.invoice,
                                  self.transactionInfo)


# register company info form to global profile edit
try:
    from socialauthapp.profile import ProfileEditForm
    from .forms import CompanyInfoForm
    ProfileEditForm.register_form(CompanyInfoForm)
except ImportError:
    pass