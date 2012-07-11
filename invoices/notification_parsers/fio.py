# coding=UTF-8
'''
Created on Jan 2, 2012

@author: vencax
'''
import re

class Parser(object):
    amountRe = re.compile(u'=C8=E1stka:[ ]*(?P<Amount>[0-9 ]+,[0-9]{1,2})')
    VSRe = re.compile(u'VS:[ ]*(?P<VS>\d+)')
    SSRe = re.compile(u'SS:[ =]*(?P<SS>\d+)')
    partnerAccountRe = re.compile('Proti=FA=E8et:[ ]*(?P<acc>[0-9]*-*[0-9]{1,10}/[0-9]{4})')
    accountRe = re.compile(u' na kont=EC:[ ]*(?P<acc>\d+)')
    inTransRe = re.compile(u'P=F8=EDjem na kont=EC')
    
    def parse(self, message):
        op = self.inTransRe.search(message)
        if op:
            transactionType = 'IN'
        else:
            transactionType = 'OUT'
        am = self.amountRe.search(message).group('Amount')
        vs = self.VSRe.search(message).group('VS')
        amount = float(am.replace(' ', '').replace(',', '.'))
        vs = int(vs)
        partnerAcc = self.partnerAccountRe.search(message).group('acc')
        accNum = '%s/2010' % self.accountRe.search(message).group('acc')
        ss = int(self.SSRe.search(message).group('SS'))
        return (transactionType, vs, ss, amount, accNum, partnerAcc, 'CZK')

if __name__ == "__main__":
    parser = Parser()
    data = u"""P=F8=EDjem na kont=EC: 2400260986 =C8=E1stka: 500,00 VS: 1\
 Zpr=E1va p=F8=EDjemci: =20 Aktu=E1ln=ED z=F9statek: 20 144,82\
 Proti=FA=E8et: 321-2500109888/2010 SS:=20 KS: 0008
"""
    print parser.parse(data)
    from test import sendTestMessage
    sendTestMessage(data, 'credit@domain.tld')