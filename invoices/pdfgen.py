'''
Created on Jun 8, 2012

@author: vencax
'''

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.utils.translation import ugettext
import datetime
from django.conf import settings
import os


class InvoicePdfGenerator(object):
    lineWidth = 12
    titleWidth = 100
    signPicture = os.path.join(settings.STATIC_ROOT, 'invoices', 'invoiceSign.png')
    
    def __init__(self, stream):
        self.p = canvas.Canvas(stream, pagesize=letter)
        
    def generate(self, invoice):
        self.p.setFont('Helvetica', 12)
        self._ds(100, 100, '%s %i' % (ugettext('invoice'), invoice.id))
        self._line(102)
        
        self._drawContractor(invoice)
        self._drawSubscriber(invoice)
        self._drawItems(invoice)
        
        self.p.setFont('Helvetica', 8)
        self.p.drawString(100, 50, '%s %s' % (ugettext('generated by'), 
                                    'django-invoices by vencax, vxk.cz'))
        # Close the PDF object cleanly, and we're done.
        self.p.showPage()
        self.p.save()
        
    def _ds(self, x, y, stringToDraw):
        self.p.drawString(x, letter[1] - y, stringToDraw)
        
    def _line(self, y):
        self.p.line(100, letter[1] - y, 500, letter[1] - y)
        
    def _drawContractor(self, invoice):
        x, y = 100, 120
        
        self._ds(x, y, ugettext('contractor'))
        y += 20
        self._ds(x, y, invoice.contractor.user.get_full_name())
        y += self.lineWidth
        self._ds(x, y, invoice.contractor.address)
        y += self.lineWidth
        self._ds(x, y, invoice.contractor.town)
        y += self.lineWidth
        self._ds(x, y, invoice.contractor.state)
        y += self.lineWidth*2
        self._ds(x, y, '%s:' % ugettext('inum'))
        self._ds(x+self.titleWidth, y, invoice.contractor.inum)
        y += self.lineWidth
        self._ds(x, y, '%s:' % ugettext('tinum'))
        self._ds(x+self.titleWidth, y, invoice.contractor.tinum or ugettext('Not tax payer'))
        y += self.lineWidth
        self._ds(x, y, '%s:' % ugettext('paymentWay'))
        self._ds(x+self.titleWidth, y, invoice.get_paymentWay_display())
        y += self.lineWidth
        self._ds(x, y, '%s:' % ugettext('variable symbol'))
        self._ds(x+self.titleWidth, y, str(invoice.id))
        y += self.lineWidth
        self._ds(x, y, '%s:' % ugettext('bankaccount'))
        self._ds(x+self.titleWidth, y, invoice.contractor.bankaccount)
    
    def _drawSubscriber(self, invoice):
        x, y = 330, 120
        self._ds(x, y, ugettext('subscriber'))
        y += 20
        self._ds(x, y, invoice.subscriber.user.get_full_name())
        y += self.lineWidth
        self._ds(x, y, invoice.subscriber.address)
        y += self.lineWidth
        self._ds(x, y, invoice.subscriber.town)
        y += self.lineWidth
        self._ds(x, y, invoice.subscriber.state)
        y += self.lineWidth*2
        self._ds(x, y, '%s:' % ugettext('inum'))
        self._ds(x+self.titleWidth, y, invoice.subscriber.inum)
        y += self.lineWidth
        self._ds(x, y, '%s:' % ugettext('tinum'))
        self._ds(x+self.titleWidth, y, invoice.subscriber.tinum or ugettext('Not tax payer'))
        y += self.lineWidth
        self._ds(x, y, ugettext('issueDate'))
        self._ds(x+self.titleWidth, y, invoice.issueDate.strftime("%d. %m. %y"))
        y += self.lineWidth
        self._ds(x, y, ugettext('dueDate'))
        dDate = invoice.issueDate + datetime.timedelta(14)                
        self._ds(x+self.titleWidth, y, dDate.strftime("%d. %m. %y"))
        y += self.lineWidth
        self._ds(x, y, ugettext('dataOfUZP'))
        self._ds(x+self.titleWidth, y, invoice.issueDate.strftime("%d. %m. %y"))
    
    def _drawItems(self, invoice):
        x, y = 100, 300
        self._ds(x, y, ugettext('name'))
        self._ds(x+300, y, ugettext('count'))
        self._ds(x+350, y, ugettext('price'))
        
        y += 4
        self._line(y)
        
        for i in invoice.items.all():
            y += self.lineWidth
            self._ds(x, y, i.name)
            self._ds(x+300, y, str(i.count))
            self._ds(x+350, y, str(i.price))
                  
        y += 4
        self._line(y)
        
        y += self.lineWidth
        self._ds(x, y, '%s:' % ugettext('TotalPrice'))
        self._ds(x+350, y, str(invoice.totalPrice()))
        
        if os.path.exists(self.signPicture):
            self.p.drawImage(self.signPicture, x+200, y)
    
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    
    class MockInvoice(object):        
        def __init__(self):
            self.contractor = {'user' : 'ABC Devel'}
            self.subscriber = {'user' : 'ZXY Consulting'}
            self.issueDate = datetime.datetime.now()
            self.id = 117
            
        def get_paymentWay_display(self):
            return 'By Account'
        
    mi = MockInvoice()
    gen = InvoicePdfGenerator()
    
    gen.generate(mi)
    