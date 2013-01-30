import os
from django.test import TestCase
from django.core.management import call_command
from invoices.models import Invoice, CompanyInfo, Item, BadIncommingTransfer
from django.conf import settings
from django.contrib.auth.models import User


class InvoiceTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        for i in range(settings.OUR_COMPANY_ID + 3):
            u = User(username='user%i' % i, last_name='Mr. %i' % i,
                     first_name='TJ', password='jfcisoa')
            u.save()
            CompanyInfo(town='town%i' % i, phone=(1000 + i), user=u).save()

        s = CompanyInfo.objects.all().order_by('?')[0]
        invoice = Invoice(subscriber=s)
        invoice.save()
        invoice.items.add(Item(name='socks', count=2, price=13))

    def testAccountNotification(self):
        """
        Test account notification command.
        """
        invoice = Invoice.objects.all().order_by('?')[0]
        mail = 'P=F8=EDjem na kont=EC: 2400260986 =C8=E1stka: %i,00 VS: %i\
 Zpr=E1va p=F8=EDjemci: =20 Aktu=E1ln=ED z=F9statek: 20 144,82\
 Proti=FA=E8et: 321-2500109888/2010 SS:=12345 KS: %i'
        baseArgs = ('credit@vpn.vxk.cz', 'automat@fio.cz')

        args = baseArgs + (
            mail % (invoice.totalPrice() - 4, invoice.id, 117),
        )
        call_command('accountNotification', *args)

        i = Invoice.objects.get(id=invoice.id)
        assert i.paid == False
        try:
            BadIncommingTransfer.objects.get(typee='l', invoice=i)
        except BadIncommingTransfer.DoesNotExist:
            raise AssertionError('BadIncommingTransfer not exists')

        args = baseArgs + (
            mail % (invoice.totalPrice() + 4, invoice.id, 117),
        )
        call_command('accountNotification', *args)

        i = Invoice.objects.get(id=invoice.id)
        assert i.paid == False
        try:
            BadIncommingTransfer.objects.get(typee='m', invoice=i)
        except BadIncommingTransfer.DoesNotExist:
            raise AssertionError('BadIncommingTransfer not exists')

        args = baseArgs + (
            mail % (invoice.totalPrice(), invoice.id, 117),
        )
        call_command('accountNotification', *args)

        i = Invoice.objects.get(id=invoice.id)
        assert i.paid == True

        # bad const symbol
        args = baseArgs + (
            mail % (invoice.totalPrice(), invoice.id, 1117),
        )
        call_command('accountNotification', *args)

        try:
            BadIncommingTransfer.objects.get(typee='u')
        except BadIncommingTransfer.DoesNotExist:
            errmess = 'BadIncommingTransfer (bad const symbol) not exists'
            raise AssertionError(errmess)

    def test_pdf_generate(self):
        """
        Tests invoice PDF generation.
        """
        outFile = '/tmp/invoice.pdf'
        i = Invoice.objects.all().order_by('?')[0]

        from invoices.mailing import _pdfInvoice
        with open(outFile, 'w') as f:
            f.write(_pdfInvoice(i))

        assert os.stat(outFile).st_size > 0
