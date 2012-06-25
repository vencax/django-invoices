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

class CompanyInfo(models.Model):
    """
    Company info describing business partner.
    """
    @classmethod
    def get_our_company_info(cls):
        return cls.objects.get(user__id=settings.OUR_COMPANY_ID)
    
    user = models.ForeignKey(User, unique=True, related_name='companyinfo')
    bankaccount = models.CharField(_('bankaccount'), max_length=32,
                                   default='00000')
    inum = models.CharField(_('inum'), max_length=32, null=True, blank=True)
    tinum = models.CharField(_('tinum'), max_length=32, null=True, blank=True)
    state = models.CharField(_('state'), max_length=3,
                             default=settings.DEFAULT_STATE_CODE)
    town = models.CharField(_('town'), max_length=32)
    zipcode = models.CharField(_('zipcode'), max_length=32,
                               default='00000')
    address = models.CharField(_('address'), max_length=64, default='00000')
    phone = models.IntegerField(_('phone'), default=0)
    
    def __unicode__(self):
        return 'Company %s' % self.user.get_full_name()
    
    def delete(self, *args, **kwargs):
        """ Do not allow to delete our company ... """
        if self.user__id != settings.OUR_COMPANY_ID:
            super(Invoice, self).delete(*args, **kwargs)


class Invoice(models.Model):
    """
    Represents an invoice.
    """
    @classmethod
    def get_default_currency(cls):
        return Thing.objects.get(code=settings.DEFAULT_CURRENCY)
    
    @classmethod
    def get_my_company_info(cls):
        return CompanyInfo.objects.get(user__id=settings.OUR_COMPANY_ID)
    
    dirChoices = [
        ('i', _('inInvoice')),
        ('o',  _('outInvoice'))
    ]
    paymentWayChoices = [
        (1,  _('cash')),
        (2,  _('transfer')),
    ]

    issueDate = models.DateField(editable=False, auto_now_add=True)
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


# register company info form to global profile edit
try:
    from socialauthapp.profile import ProfileEditForm
    from .forms import CompanyInfoForm
    ProfileEditForm.register_form(CompanyInfoForm)
except ImportError:
    pass