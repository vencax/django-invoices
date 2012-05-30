from django.contrib import admin
from models import Item, Invoice, BadIncommingTransfer
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ItemsInline(admin.TabularInline):
    model = Item
    extra = 1
    
def totalPrice(obj):
    return '%.2f %s' % (obj.totalPrice(), settings.DEFAULT_CURRENCY)
totalPrice.short_description = _('TotalPrice')

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]
    list_filter = ['partner']
    list_display = ['issueDate', 'partner', 'typee', totalPrice, 'paid']
    list_filter = ['paid', 'typee']
    date_hierarchy = 'issueDate'
  
class BadIncommingTransferAdmin(admin.ModelAdmin):
    list_filter = ['typee']
    list_display = ['typee', 'invoice']

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(BadIncommingTransfer, BadIncommingTransferAdmin)