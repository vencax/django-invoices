'''
Created on Jun 18, 2012

@author: vencax
'''
from django import forms
from .models import CompanyInfo

class CompanyInfoForm(forms.ModelForm):
    """ special form for user edit page """
    class Meta:
        model = CompanyInfo
        exclude = ('user', )
        
    def __init__(self, **kwargs):
        u = kwargs.pop('instance')
        try:
            ci = CompanyInfo.objects.get(user=u)
        except CompanyInfo.DoesNotExist:
            ci = CompanyInfo(user=u)
            ci.save()
            
        kwargs['instance'] = ci            
        
        super(CompanyInfoForm, self).__init__(**kwargs)