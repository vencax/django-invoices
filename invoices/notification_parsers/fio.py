# coding=UTF-8
'''
Created on Jan 2, 2012

@author: vencax
'''
from test import sendTestMessage
import re

class Parser(object):
  amountRe = re.compile(r'Částka:[ ]*(?P<Amount>[0-9,]+)')
  VSRe = re.compile(r'VS:[ ]*(?P<VS>\d+)')
  
  def parse(self, message):
    am = self.amountRe.search(message).group('Amount')
    vs = self.VSRe.search(message).group('VS')
    amount = float(am.replace(',', '.'))
    vs = int(vs)
    return (vs, amount)

if __name__ == "__main__":
  sendTestMessage("""
Výdaj na kontě: 2500109888
Částka: 640,80
VS: 1
US:  ALBERT HM 2799 PRAH
Aktuální zůstatek: 739,94
Protiúčet: platba kartou
SS: 6761657716
KS:
""")