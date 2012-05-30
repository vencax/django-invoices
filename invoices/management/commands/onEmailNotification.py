'''
Created on Dec 29, 2011

@author: vencax
'''
from django.core.management.base import BaseCommand
import logging

class Command(BaseCommand):
    args = ''
    help = 'parses incoming mail and takes actions base on it'
    
    def handle(self, *args, **options):
        logging.basicConfig()
        