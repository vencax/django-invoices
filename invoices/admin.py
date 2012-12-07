from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from models import Item, Invoice, BadIncommingTransfer, \
    CompanyInfo, RecurringInvoice
from mailing import downloadInvoices


class ItemsInline(admin.TabularInline):
    model = Item
    extra = 1


def totalPrice(obj):
    return '%.2f %s' % (obj.totalPrice(), settings.DEFAULT_CURRENCY)
totalPrice.short_description = _('TotalPrice')


def downloadAsPDF(modeladmin, request, queryset):
    return downloadInvoices(queryset, request)
downloadAsPDF.short_description = _('download as PDF')


def sendInvoices(modeladmin, request, queryset):
    for i in queryset:
        i.send()
sendInvoices.short_description = _('send invoices')


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]
    list_display = ['issueDate', 'contractor', 'subscriber', 'direction',
                    totalPrice, 'paid']
    list_filter = ['paid', 'direction']
    date_hierarchy = 'issueDate'
    actions = [downloadAsPDF, sendInvoices]

    def queryset(self, request):
        q = super(InvoiceAdmin, self).queryset(request)
        if not request.user.is_superuser:
            q.filter(partner__exact=request.user)
        return q


class BadIncommingTransferAdmin(admin.ModelAdmin):
    list_filter = ['typee']
    list_display = ['typee', 'invoice']


class CompanyInfoAdmin(admin.ModelAdmin):
    search_fields = ['town', 'user__first_name', 'zipcode', 'inum']
    list_filter = ['state']
    list_display = ['user', 'state', 'address', 'town', 'zipcode', 'inum']


class RecurringInvoiceAdmin(admin.ModelAdmin):
    list_filter = ('frequency', )
    list_display = ('template', 'frequency', 'autosend')

admin.site.register(CompanyInfo, CompanyInfoAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(BadIncommingTransfer, BadIncommingTransferAdmin)
admin.site.register(RecurringInvoice, RecurringInvoiceAdmin)
