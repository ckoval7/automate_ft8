#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import threading
import subprocess
import os
import re
from datetime import datetime
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('./ft8_qso.conf')

my_call = str(parser.get('main', 'my_call_sign'))
my_grid = str(parser.get('main', 'my_grid_square'))
tx_cycle = str(parser.get('main', 'transmit_cycle'))
rx_cycle = str(parser.get('main', 'receive_cycle'))
calling_cq = True
retry = 0
their_call = ''
their_grid = ''
snr = ''
their_msg = ''

def tx():
    global tx_cycle
    while True:
        print("Starting TX")
        os.system('python ft8_tx.py '+tx_cycle)# 2> /dev/null')
        time.sleep(8)
        print("Exiting TX")

def rx():
    global rx_cycle
    while True:
        print("Starting RX")
        os.system('python ft8_rx.py '+rx_cycle)# 2> /dev/null')
        parse_rx()
        time.sleep(8)
        print("Exiting RX")


class qso_tracker:
    def __init__(self,current_call,step,max_step):
        self.current_call = ''
        self.step = 1
        self.max_step = 3

def tx_cq(my_call, my_grid):
    os.system('./ft8encode "CQ '+my_call+' '+my_grid+'" 1000 0 0 0 0 1 47')

def tx_report(their_call, my_call, snr):
    if int(snr) > 0:      #Add + if the number is positive
        os.system('./ft8encode "'+their_call+' '+my_call+' +'+str(snr).zfill(2)+'" 1000 0 0 0 0 1 47')
    else:
        os.system('./ft8encode "'+their_call+' '+my_call+' '+str(snr).zfill(2)+'" 1000 0 0 0 0 1 47')

def tx_73(their_call, my_call):
    os.system('./ft8encode "'+their_call+' '+my_call+' RR73" 1000 0 0 0 0 1 47')

def chk_blacklist(their_call):
    blacklist = open('./captures/blacklist.txt',"r+")
    check_blacklist = blacklist.readlines()
    blacklist.close()
    for line in check_blacklist:
        if their_call in line:
            return True
        else:
            return False

def parse_rx():
    global calling_cq
    global retry
    now = datetime.now()
    rx_time = now.strftime("[%m/%d/%Y %H:%M:%S]")
    try:
        ft8_decode = subprocess.check_output('./ft8decode 300 3000 10 ./ft8rx.wav', shell=True)
        print(ft8_decode)
        qso_list = open('./captures/text_rx.txt',"a+")
        qso_list.write(rx_time+' '+ft8_decode)
        qso_list.close()
        collapsedstring = ' '.join(ft8_decode.split())
        snr = collapsedstring.split(' ')[0] #The first number is always the SNR
        #In a properly formatted message this will be the receiver's call sign
        rx_my_call = collapsedstring.split(' ')[6]
        #In a properly formatted message this should always be the senders call sign
        their_call = collapsedstring.split(' ')[7]
        #This position will either be a grid square (e.g. FM19), a signal report (e.g. -10 or R-10), "RR73", or "73", which closes the QSO
        their_msg = collapsedstring.split(' ')[8]
    except:
        print("No Reply")
        rx_my_call = ''

    if (rx_my_call == my_call
    and qso_tracker.current_call == (their_call or '')
    and not chk_blacklist(their_call)):
        if re.search("[A-R]{2}\d{2}", their_grid) and qso_tracker.step == 1:
            tx_report(their_call, my_call, snr)
            calling_cq = False
            retry = 0
            qso_tracker.step = 2
            qso_tracker.current_call = their_call
        elif re.search("[R][+|-]\d{2}", their_msg) and qso_tracker.step == 2:
            tx_73(their_call, my_call)
            calling_cq = False
            retry = 0
            qso_tracker.step = 3
        elif their_msg == "73" and qso_tracker.step == 3:
            tx_cq(my_call, their_call)
            calling_cq = True
            retry = 0
            qso_tracker.step = 1
            blacklist = open('./captures/blacklist.txt',"a+")
            blacklist.write(qso_tracker.current_call)
            blacklist.close()
            #award points
            qso_tracker.current_call = ''
        else:
            tx_cq(my_call, my_grid)
    else:
      #repeat last action, up to 4 times if not cq
        if not calling_cq and retry < 4:
            retry += 1
        elif not calling_cq and retry >= 4:
            tx_cq(my_call, my_grid)
            retry = 0
            calling_cq = True
        else:
            print("Calling CQ")
            calling_cq = True

def main():
    tx_cq(my_call, my_grid)
    t = threading.Thread(name='Transmit', target=tx)
    r = threading.Thread(name='Receive', target=rx)
    t.daemon = True
    r.daemon = True
    t.start()
    r.start()
    raw_input("\n\nPress Enter to Exit: ")
    #t.join()
    #r.join()
    quit()

if __name__== "__main__":
    main()