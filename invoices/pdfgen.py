
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.utils.translation import ugettext
from reportlab.lib import styles
from reportlab.platypus import (Paragraph, Table, Image, Frame,
                                PageTemplate, Spacer)
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus.flowables import HRFlowable
from reportlab.platypus.tables import TableStyle
from reportlab.pdfgen.canvas import Canvas
from invoices.signals import INVOICE_PAY_SYMBOL


class InvoicePdfGenerator(object):
    """
    This class can print an invoice object into PDF stream.
    """

    def __init__(self, signPicture, fontfile, extraContractorText=None,
                 highlightColor=(1, 0, 0)):
        try:
            pdfmetrics.registerFont(TTFont('custom', fontfile))
            self.font = 'custom'
        except:
            self.font = 'Courier'

        self._preapareStyles(self.font, highlightColor)
        self.extraContractorText = extraContractorText
        self.signPicture = signPicture
        self.doc = self.prepareDoc()

    def prepareDoc(self):
        rightMargin, leftMargin, topMargin, bottomMargin = 72, 72, 72, 18

        doc = SimpleDocTemplate(None, pagesize=A4,
            rightMargin=rightMargin, leftMargin=leftMargin,
            topMargin=topMargin, bottomMargin=bottomMargin)

        frameWidth = doc.width / 2
        headerHeight = 50
        userInfoHeight = 228
        itemsFrameHeight = doc.height - userInfoHeight - headerHeight

        header = Frame(leftMargin, doc.height, doc.width, headerHeight)
        column1 = Frame(leftMargin, doc.height - userInfoHeight,
                        frameWidth, userInfoHeight)
        column2 = Frame(leftMargin + frameWidth, doc.height - userInfoHeight,
                        frameWidth, userInfoHeight)
        items = Frame(leftMargin,
                      doc.height - userInfoHeight - itemsFrameHeight,
                      doc.width, itemsFrameHeight)

        template = PageTemplate(frames=[header, column1, column2, items])
        doc.addPageTemplates(template)

        half = doc.width / 2
        self.columnWidths = (half / 2, half / 2)

        self.itemColumnWidths = (
            (float(2) / 3) * doc.width,
            (float(1) / 3) * doc.width * (float(1) / 3),
            (float(1) / 3) * doc.width * (float(2) / 3)
        )

        return doc

    def generate(self, invoice, stream):
        title = '%s %s' % (ugettext('invoice'), invoice.getNumber())
        self.doc.title = title
        content = []

        content.append(Paragraph(title, self.styles['Heading1']))
        content.append(HRFlowable(width='100%'))

        self._drawContractor(invoice, content)
        self._drawSubscriber(invoice, content)

        self._drawItems(invoice, content)

        if os.path.exists(self.signPicture):
            content.append(Image(self.signPicture, 5 * cm, 2 * cm))

        content.append(HRFlowable(width='100%'))
        genBy = '%s django-invoices | vxk.cz' % ugettext('generated by')
        content.append(Paragraph(genBy, self.styles['genBy']))

        self.doc.filename = stream
        self.doc.build(content, canvasmaker=self._makeCanvas)

    def _makeCanvas(self, filename, **kwargs):
        c = Canvas(filename, **(kwargs))
        c.setEncrypt('utf-8')
        return c

    def _drawContractor(self, invoice, content, **kwargs):
        content.append(Paragraph(ugettext('contractor').upper(),
                                 self.styles['Heading4']))

        tabledata = self._draw_user_info(content, invoice.contractor,
                                         extra=self.extraContractorText)

        self._draw_labeled('paymentWay',
                           invoice.get_paymentWay_display(), tabledata)
        self._draw_labeled('variable symbol', str(invoice.id), tabledata)
        self._draw_labeled('specific symbol', str(INVOICE_PAY_SYMBOL),
                           tabledata)
        self._draw_labeled('bankaccount',
                           invoice.contractor.bankaccount, tabledata)

        content.append(self._createInfoTable(tabledata))

    def _createInfoTable(self, data):
        t = Table(data, colWidths=self.columnWidths)
        maxindex = (len(data[0]) - 1, len(data) - 1)
        t.setStyle(TableStyle([('FONT', (0, 0), maxindex, self.font, 8)]))
        return t

    def _drawSubscriber(self, invoice, content):
        content.append(Paragraph(ugettext('subscriber').upper(),
                                 self.styles['Heading4']))

        tabledata = self._draw_user_info(content, invoice.subscriber)

        self._draw_labeled('issueDate',
            invoice.issueDate.strftime("%d. %m. %Y"), tabledata)
        self._draw_labeled('dueDate',
            invoice.dueDate.strftime("%d. %m. %Y"), tabledata)

        self._drawDUZP(invoice, tabledata)

        tabledata.append([])    # compensation to contractor info lines
        tabledata.append([])

        content.append(self._createInfoTable(tabledata))

    def _drawDUZP(self, invoice, tabledata):
        if invoice.contractor.tinum:
            self._draw_labeled('dataOfUZP',
                invoice.issueDate.strftime("%d. %m. %Y"), tabledata)
        else:
            tabledata.append([])

    def _drawItems(self, invoice, content):
        data = []
        data.append([ugettext('name'), ugettext('count'), ugettext('price')])

        for i in invoice.items.all():
            data.append([i.name, str(i.count),
                         self._printMoney(i.price, invoice)])

        t = Table(data, colWidths=self.itemColumnWidths)
        maxindex = (len(data[0]) - 1, len(data) - 1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.Color(0, 0, 0, 0.1)),
            ('FONT', (0, 0), maxindex, self.font, 8)
        ]))
        content.append(t)

        content.append(Paragraph('%s: %s' % (
            ugettext('TotalPrice'),
            self._printMoney(invoice.totalPrice(), invoice)
        ), self.styles['Heading2']))

    def _draw_labeled(self, label, data, content):
        content.append(['%s:' % ugettext(label), data])

    def _draw_user_info(self, content, userinfo, **kwargs):
        content.append(Paragraph(userinfo.user.get_full_name(),
                                 self.styles['Heading3']))
        content.append(Paragraph(userinfo.address, self.styles['Heading4']))
        content.append(Paragraph(userinfo.town, self.styles['Heading4']))
        content.append(Paragraph(userinfo.state, self.styles['Heading4']))

        if 'extra' in kwargs and kwargs['extra']:
            content.append(Paragraph(kwargs['extra'],
                                     self.styles['Normal']))
        else:
            content.append(Spacer(1, 12))

        tabledata = []
        self._draw_labeled('inum', userinfo.inum, tabledata)
        tinum = userinfo.tinum or ugettext('Not tax payer')
        self._draw_labeled('tinum', tinum, tabledata)
        return tabledata

    def _printMoney(self, value, invoice):
        return ('%.2f %s' % (value, invoice.currency.code)).replace('.', ',')

    def _preapareStyles(self, fontName, highlightColor):
        self.styles = styles.StyleSheet1()

        c = colors.Color(*(highlightColor + (1, )))

        self.styles.add(styles.ParagraphStyle(name='Normal',
            fontName=fontName, fontSize=10, leading=12))

        self.styles.add(styles.ParagraphStyle(name='Heading1',
            parent=self.styles['Normal'], fontSize=18, leading=22,
            spaceAfter=6), alias='h1')

        self.styles.add(styles.ParagraphStyle(name='Heading2',
            parent=self.styles['Normal'], fontSize=14, leading=18,
            spaceBefore=12, spaceAfter=6), alias='h2')

        self.styles.add(styles.ParagraphStyle(name='Heading3',
            parent=self.styles['Normal'], fontSize=12, leading=14,
            spaceBefore=12, spaceAfter=6, textColor=c), alias='h3')

        self.styles.add(styles.ParagraphStyle(name='Heading4',
            parent=self.styles['Normal'], fontSize=10, leading=12,
            spaceBefore=10, spaceAfter=4), alias='h4')

        self.styles.add(styles.ParagraphStyle(name='genBy', fontSize=8,
                                              parent=self.styles['Normal']))
