from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from .views import InvoiceView

urlpatterns = patterns('',
    url(r'^invoice/(?P<invoice_id>\d+)/',
        login_required(InvoiceView.as_view()),
        name='invoice_detail'),
)
