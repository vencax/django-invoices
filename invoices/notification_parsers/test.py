'''
Created on Jan 2, 2012

@author: vencax
'''
def sendTestMessage(msg):
  fromAddr = 'banka@banka.cz'
  toAddrs = ['ahoj@koko.cz']
  
  message = ("From: %s\r\nTo: %s\r\n\r\n" % (fromAddr, ", ".join(toAddrs)))
  message += msg
  message += '\r\n'
  
  import smtplib
  c = smtplib.SMTP('localhost', 2525)
  c.sendmail(fromAddr, toAddrs, msg)
  c.quit()