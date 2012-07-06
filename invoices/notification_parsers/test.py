'''
Created on Jan 2, 2012

@author: vencax
'''
def sendTestMessage(msg, to):
    fromAddr = 'banka@banka.cz'
    toAddrs = [to]
    
    message = ('From: %s\r\nTo: %s\r\n\r\n' % (fromAddr, ','.join(toAddrs)))
    message += msg
    message += '\r\n'
    
    import smtplib
    c = smtplib.SMTP('localhost', 25)
    c.sendmail(fromAddr, toAddrs, msg)
    c.quit()