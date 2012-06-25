'''
Created on May 30, 2012

@author: vencax
'''

def invoice_saved(instance, sender, **kwargs):
    """
    Called on invoice save. It can generate payment request if the invoice
    is incoming. Or notify partner if the invoice is outgoing.
    """
    pass
