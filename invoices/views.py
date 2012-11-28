

from django.views.generic.base import TemplateView


class InvoiceView(TemplateView):
    template_name = 'bistro/index.html'

    def get_context_data(self, **kwargs):
        return {'invoice': 'jidlo/output/'}
