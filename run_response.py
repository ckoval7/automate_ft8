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
responding = False
retry = 0
their_call = ''
their_grid = ''
snr = ''
their_msg = ''


def tx(stop_tx):
    while not stop_tx.isSet():
        print("\nStarting TX")
        os.system('python ft8_tx.py ' + tx_cycle)  # 2> /dev/null')
        time.sleep(8)
        print("\nExiting TX")


def rx(stop_rx):
    while not stop_rx.isSet():
        print("\nStarting RX")
        os.system('python ft8_rx.py ' + rx_cycle)  # 2> /dev/null')
        parse_rx()
        time.sleep(8)
        print("\nExiting RX")


class qso_tracker:
    def __init__(self, current_call, step):
        self.current_call = current_call
        self.step = step
        self.max_step = 4


def answer_cq(their_call, my_call, my_grid):
    os.system('./ft8encode "' + their_call + ' ' + my_call + ' ' + my_grid + '" 1000 0 0 0 0 1 47')
    print("\nAnswering CQ")


def tx_report(their_call, my_call, snr):
    if int(snr) > 0:  # Add + if the number is positive
        os.system('./ft8encode "' + their_call + ' ' + my_call + ' R+' + str(snr).zfill(2) + '" 1000 0 0 0 0 1 47')
    else:
        os.system('./ft8encode "' + their_call + ' ' + my_call + ' R' + str(snr).zfill(2) + '" 1000 0 0 0 0 1 47')
    print("\nSending Report")


def tx_73(their_call, my_call):
    os.system('./ft8encode "' + their_call + ' ' + my_call + ' 73" 1000 0 0 0 0 1 47')
    print("\nSending 73")


def chk_blacklist(their_call):
    try:
        blacklist = open('./captures/blacklist.txt', "r+")
        check_blacklist = blacklist.readlines()
        blacklist.close()
        for line in check_blacklist:
            if their_call in line:
                return True
            else:
                return False
    except:
        return False


def parse_rx():
    global responding
    global retry
    global qso
    global their_call
    global snr
    global their_msg
    global stop_rx
    global stop_tx
    global t

    now = datetime.now()
    rx_time = now.strftime("[%m/%d/%Y %H:%M:%S]")
    replies = []
    try:
        ft8_decode = subprocess.check_output('./ft8decode 300 3000 3 ./ft8rx.wav', shell=True)
        print("\n" + ft8_decode)
        if ft8_decode != '':
            qso_list = open('./captures/text_rx.txt', "a+")
            qso_list.write(rx_time + ' ' + ft8_decode)
            qso_list.close()
        for line in range(len(ft8_decode_lines)):
            if responding:
                if qso.current_call in ft8_decode_lines[line]:
                    collapsedstring = ' '.join(ft8_decode_lines[line].split())
                    # print(collapsedstring)
                    replies.append(collapsedstring.split(' '))
            else:
                collapsedstring = ' '.join(ft8_decode_lines[line].split())
                # print(collapsedstring)
                replies.append(collapsedstring.split(' '))
        # print(replies)
        chosen_reply = max(replies, key=lambda x: x[1])
        print(chosen_reply)
        snr = chosen_reply[1]  # The second number is always the SNR
        # In a properly formatted message this will be the receiver's call sign
        rx_my_call = chosen_reply[6]
        # In a properly formatted message this should always be the senders call sign
        their_call = chosen_reply[7]
        # This position will either be a grid square (e.g. FM19), a signal report (e.g. -10 or R-10),
        # "RR73", or "73", which closes the QSO
        their_msg = chosen_reply[8]
    #        collapsedstring = ' '.join(ft8_decode.split())
    #        snr = collapsedstring.split(' ')[1] #The second number is always the SNR
    #        print('[1]'+snr)
    #        #In a properly formatted message this will be the receiver's call sign
    #        rx_my_call = collapsedstring.split(' ')[6]
    #        print('[6]'+rx_my_call)
    #        #In a properly formatted message this should always be the senders call sign
    #        their_call = collapsedstring.split(' ')[7]
    #        print('[7]'+their_call)
    #        #This position will either be a grid square (e.g. FM19), a signal report (e.g. -10 or R-10),
    #        "RR73", or "73", which closes the QSO
    #        their_msg = collapsedstring.split(' ')[8]
    #        print('[8]'+their_msg)
    except:
        print("\nNo Statons Calling")
        chosen_reply = ''
        rx_my_call = ''

    rules = [chosen_reply != '',
             rx_my_call == my_call or 'CQ',
             qso.current_call == their_call or 'NOCALL',
             not chk_blacklist(their_call)]
    if all(rules):
        if not t.isAlive():
            t.start()
        if their_msg != 'RR73' and re.search("[A-R]{2}\d{2}", their_msg):  # and qso.step == 1:
            if qso.step == 1:
                answer_cq(their_call, my_call, my_grid)
                responding = True
                retry = 0
                qso.step = 2
                qso.current_call = their_call
            else:
                print("\nResponding again...")
        elif re.search("[+|-]\d{2}", their_msg):  # and qso.step == 2:
            if qso.step == 2:
                tx_report(their_call, my_call, snr)
                responding = True
                retry = 0
                qso.step = 3
            else:
                print("\nResending Report")
        elif their_msg == "RR73" or "RRR":  # and qso.step == 3:
            if qso.step == 3:
                tx_73(their_call, my_call)
                responding = False
                retry = 0
                qso.step = 1
                blacklist = open('./captures/blacklist.txt', "a+")
                blacklist.write(qso.current_call + "\n")
                blacklist.close()
                qso.current_call = 'NOCALL'
            else:
                stop_tx.set()
                t.join()
    else:
        # repeat last action, up to 4 times
        if responding and retry < 4:
            retry += 1
        elif responding and retry >= 4:
            retry = 0
            responding = False
            stop_tx.set()
            t.join()
        else:
            print("\nListening...")
            responding = False
            if t.isAlive():
                stop_tx.set()
                t.join()


def main():
    global t
    global stop_rx
    global stop_tx
    stop_rx = threading.Event()
    stop_tx = threading.Event()
    t = threading.Thread(name='Transmit', target=tx, args=(stop_tx,))
    r = threading.Thread(name='Receive', target=rx, args=(stop_rx,))
    t.daemon = True
    r.daemon = True
    r.start()
    raw_input("\n\nPress Enter to Exit:\n\n")
    print("\n\nKilling threads, please wait for TX/RX cycles to complete...\n\n")
    stop_rx.set()
    stop_tx.set()
    if t.isAlive():
        t.join()
    r.join()
    quit()


qso = qso_tracker('NOCALL', 1)
if __name__ == "__main__":
    main()
