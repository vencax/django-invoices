from django.contrib import admin
from models import Item, Invoice, BadIncommingTransfer, CompanyInfo
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

    def queryset(self, request):
        q = super(InvoiceAdmin, self).queryset(request)
        if not request.user.is_superuser:
            q.filter(partner__exact=request.user)
        return q

class BadIncommingTransferAdmin(admin.ModelAdmin):
    list_filter = ['typee']
    list_display = ['typee', 'invoice']

class CompanyInfoAdmin(admin.ModelAdmin):
    search_fields = ['town', 'user__first_name' ]
    list_filter = ['state']
    list_display = ['user', 'state', 'town']


admin.site.register(CompanyInfo, CompanyInfoAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(BadIncommingTransfer, BadIncommingTransferAdmin)

