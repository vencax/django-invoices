# coding=UTF-8
'''
Created on Jan 2, 2012

@author: vencax
'''
import re
from test import sendTestMessage

class Parser(object):
    amountRe = re.compile(u'Částka:[ ]*(?P<Amount>[0-9,]+)')
    VSRe = re.compile(u'VS:[ ]*(?P<VS>\d+)')
    SSRe = re.compile(u'SS:[ ]*(?P<SS>\d+)')
    accountRe = re.compile(u'Výdaj na kontě:[ ]*(?P<acc>\d+)')
    
    def parse(self, message):
        am = self.amountRe.search(message).group('Amount')
        vs = self.VSRe.search(message).group('VS')
        amount = float(am.replace(',', '.'))
        vs = int(vs)
        accNum = '%s/2010' % self.accountRe.search(message).group('acc')
        ss = int(self.SSRe.search(message).group('SS'))
        return (vs, ss, amount, accNum, 'CZK')

if __name__ == "__main__":
    parser = Parser()
    data = u"""
Výdaj na kontě: 2500109888 Částka: 640,80 VS: 1 US: \
ALBERT HM 2799 PRAH Aktuální zůstatek: 739,94 \
Protiúčet: platba kartou SS: 6761657716 KS:
"""
    print parser.parse(data)
    sendTestMessage(data)