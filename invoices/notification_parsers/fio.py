# coding=UTF-8
import re


class Parser(object):
    """
    Parses mail content fio FIO bank.
    """

    amountRe = re.compile(u'=C8=E1stka:[ ]*(?P<GNAME>[0-9 ]+,[0-9]{1,2})')
    VSRe = re.compile(u'VS:[ ]*(?P<GNAME>\d+)')
    SSRe = re.compile(u'SS:[ =]*(?P<GNAME>\d+)')
    KSRe = re.compile(u'KS:[ =]*(?P<GNAME>\d+)')
    partnerAccountRe = re.compile('Proti=FA=E8et:[ ]*\
(?P<GNAME>[0-9]*-*[0-9]{1,10}/[0-9]{4})')
    accountRe = re.compile(u' na kont=EC:[ ]*(?P<GNAME>\d+)')
    inTransRe = re.compile(u'P=F8=EDjem na kont=EC')

    def parse(self, message):
        direction = 'IN' if self.inTransRe.search(message) else 'OUT'
        amount = float(self._val_or_none(self.amountRe, message).\
                   replace(' ', '').replace(',', '.'))

        vs = self._val_or_none(self.VSRe, message, lambda x: int(x))
        partnerAcc = self._val_or_none(self.partnerAccountRe, message)
        accNum = '%s/2010' % self._val_or_none(self.accountRe, message)
        ss = self._val_or_none(self.SSRe, message, lambda x: int(x))
        ks = self._val_or_none(self.KSRe, message, lambda x: int(x))
        return {
            'direction': direction,
            'varSymb': vs,
            'specSymb': ss,
            'constSymb': ks,
            'amount': amount,
            'sourceAcc': accNum,
            'destAcc': partnerAcc,
            'currency': 'CZK'
        }

    def _val_or_none(self, regexp, line, transfunc=lambda x: x):
        try:
            return transfunc(regexp.search(line).group('GNAME'))
        except Exception:
            return None

if __name__ == "__main__":
    parser = Parser()
    data = u"""P=F8=EDjem na kont=EC: 2400260986 =C8=E1stka: 100,00 VS: 19\
 Zpr=E1va p=F8=EDjemci: =20 Aktu=E1ln=ED z=F9statek: 20 144,82\
 Proti=FA=E8et: 321-2500109888/2010 SS:=20 KS: 0008
"""
    print parser.parse(data)

    weirddata = u"""P=F8=EDjem na kont=EC: 2400260986 =C8=E1stka: 100,00\
 VS: 19 Zpr=E1va p=F8=EDjemci: =20 Aktu=E1ln=ED z=F9statek: 20 144,82\
 Proti=FA=E8et: 321-2500109888/2010 SS:=
"""
    print parser.parse(weirddata)
