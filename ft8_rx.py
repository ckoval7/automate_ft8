#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: SSB Receiver and Recorder
# Author: K3CPK
# Description: Simple SSB receiver
# GNU Radio version: 3.7.13.5
##################################################

from datetime import datetime
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import ConfigParser
import osmosdr
import time
import sys

try:
    cycle = sys.argv[1]
except:
    cycle = 'even'

class ssb_rx_rec(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "SSB Receiver and Recorder")

        ##################################################
        # Variables
        ##################################################
        self.file_name = file_name = "./ft8_qso.conf"
        self._wav_save_config = ConfigParser.ConfigParser()
        self._wav_save_config.read(file_name)
        try: wav_save = self._wav_save_config.get('rx', 'rx_wav_file')
        except: wav_save = 'ft8rx.wav'
        self.wav_save = wav_save
        self._rf_samp_rate_config = ConfigParser.ConfigParser()
        self._rf_samp_rate_config.read(file_name)
        try: rf_samp_rate = self._rf_samp_rate_config.getfloat('rx', 'rf_sample_rate')
        except: rf_samp_rate = 2.4e6
        self.rf_samp_rate = rf_samp_rate
        self.xlate_filter_taps = xlate_filter_taps = firdes.low_pass(1, rf_samp_rate, 125000, 25000, firdes.WIN_HAMMING, 6.76)
        self._wav_samp_rate_config = ConfigParser.ConfigParser()
        self._wav_samp_rate_config.read(file_name)
        try: wav_samp_rate = self._wav_samp_rate_config.getfloat('rx', 'wav_sample_rate')
        except: wav_samp_rate = 12e3
        self.wav_samp_rate = wav_samp_rate
        self._rx_ppm_config = ConfigParser.ConfigParser()
        self._rx_ppm_config.read(file_name)
        try: rx_ppm = self._rx_ppm_config.getfloat('rx', 'rx_sdr_ppm')
        except: rx_ppm = 0
        self.rx_ppm = rx_ppm
        self._rx_dev_config = ConfigParser.ConfigParser()
        self._rx_dev_config.read(file_name)
        try: rx_dev = self._rx_dev_config.get('rx', 'rx_device_string')
        except: rx_dev = 'rtl=0'
        self.rx_dev = rx_dev
        self._rf_gain_config = ConfigParser.ConfigParser()
        self._rf_gain_config.read(file_name)
        try: rf_gain = self._rf_gain_config.getfloat('rx', 'rx_rf_gain')
        except: rf_gain = 25.4
        self.rf_gain = rf_gain
        self.recfile = recfile = wav_save
        self.prefix = prefix = "./captures/"
        self._offset_config = ConfigParser.ConfigParser()
        self._offset_config.read(file_name)
        try: offset = self._offset_config.getfloat('rx', 'rx_offset')
        except: offset = 5e3
        self.offset = offset
        self.low = low = 300
        self._if_samp_rate_config = ConfigParser.ConfigParser()
        self._if_samp_rate_config.read(file_name)
        try: if_samp_rate = self._if_samp_rate_config.getfloat('rx', 'if_sample_rate')
        except: if_samp_rate = 48e3
        self.if_samp_rate = if_samp_rate
        self._if_gain_config = ConfigParser.ConfigParser()
        self._if_gain_config.read(file_name)
        try: if_gain = self._if_gain_config.getfloat('rx', 'if_gain')
        except: if_gain = 0
        self.if_gain = if_gain
        self.high = high = 2.7e3
        self._freq_config = ConfigParser.ConfigParser()
        self._freq_config.read(file_name)
        try: freq = self._freq_config.getfloat('rx', 'rx_freq')
        except: freq = 144.174e6
        self.freq = freq
        self._bb_gain_config = ConfigParser.ConfigParser()
        self._bb_gain_config.read(file_name)
        try: bb_gain = self._bb_gain_config.getfloat('rx', 'bb_gain')
        except: bb_gain = 0
        self.bb_gain = bb_gain

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=int(wav_samp_rate),
                decimation=int(if_samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + rx_dev )
        self.osmosdr_source_0.set_sample_rate(rf_samp_rate)
        self.osmosdr_source_0.set_center_freq(freq-offset, 0)
        self.osmosdr_source_0.set_freq_corr(rx_ppm, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(rf_gain, 0)
        self.osmosdr_source_0.set_if_gain(if_gain, 0)
        self.osmosdr_source_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (xlate_filter_taps), offset, rf_samp_rate)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(recfile, 1, 12000, 16)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.band_pass_filter = filter.fir_filter_ccc(int(rf_samp_rate/if_samp_rate), firdes.complex_band_pass(
        	1, rf_samp_rate, low, high, 500, firdes.WIN_HAMMING, 6.76))
        self.analog_agc2_xx_0 = analog.agc2_cc(0.1, 50e-6, 0.8, 1.0)
        self.analog_agc2_xx_0.set_max_gain(1)
        self.head = blocks.head(gr.sizeof_float*1, 12000*15)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc2_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.band_pass_filter, 0), (self.analog_agc2_xx_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.head, 0))
        self.connect((self.head, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.band_pass_filter, 0))
        self.connect((self.osmosdr_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_real_0, 0))

    def get_file_name(self):
        return self.file_name

    def set_file_name(self, file_name):
        self.file_name = file_name
        self._wav_samp_rate_config = ConfigParser.ConfigParser()
        self._wav_samp_rate_config.read(self.file_name)
        if not self._wav_samp_rate_config.has_section('rx'):
        	self._wav_samp_rate_config.add_section('rx')
        self._wav_samp_rate_config.set('rx', 'wav_sample_rate', str(None))
        self._wav_samp_rate_config.write(open(self.file_name, 'w'))
        self._rx_ppm_config = ConfigParser.ConfigParser()
        self._rx_ppm_config.read(self.file_name)
        if not self._rx_ppm_config.has_section('rx'):
        	self._rx_ppm_config.add_section('rx')
        self._rx_ppm_config.set('rx', 'rx_sdr_ppm', str(None))
        self._rx_ppm_config.write(open(self.file_name, 'w'))
        self._rx_dev_config = ConfigParser.ConfigParser()
        self._rx_dev_config.read(self.file_name)
        if not self._rx_dev_config.has_section('rx'):
        	self._rx_dev_config.add_section('rx')
        self._rx_dev_config.set('rx', 'rx_device_string', str(None))
        self._rx_dev_config.write(open(self.file_name, 'w'))
        self._rf_samp_rate_config = ConfigParser.ConfigParser()
        self._rf_samp_rate_config.read(self.file_name)
        if not self._rf_samp_rate_config.has_section('rx'):
        	self._rf_samp_rate_config.add_section('rx')
        self._rf_samp_rate_config.set('rx', 'rf_sample_rate', str(None))
        self._rf_samp_rate_config.write(open(self.file_name, 'w'))
        self._rf_gain_config = ConfigParser.ConfigParser()
        self._rf_gain_config.read(self.file_name)
        if not self._rf_gain_config.has_section('rx'):
        	self._rf_gain_config.add_section('rx')
        self._rf_gain_config.set('rx', 'rx_rf_gain', str(None))
        self._rf_gain_config.write(open(self.file_name, 'w'))
        self._offset_config = ConfigParser.ConfigParser()
        self._offset_config.read(self.file_name)
        if not self._offset_config.has_section('rx'):
        	self._offset_config.add_section('rx')
        self._offset_config.set('rx', 'rx_offset', str(None))
        self._offset_config.write(open(self.file_name, 'w'))
        self._if_samp_rate_config = ConfigParser.ConfigParser()
        self._if_samp_rate_config.read(self.file_name)
        if not self._if_samp_rate_config.has_section('rx'):
        	self._if_samp_rate_config.add_section('rx')
        self._if_samp_rate_config.set('rx', 'if_sample_rate', str(None))
        self._if_samp_rate_config.write(open(self.file_name, 'w'))
        self._if_gain_config = ConfigParser.ConfigParser()
        self._if_gain_config.read(self.file_name)
        if not self._if_gain_config.has_section('rx'):
        	self._if_gain_config.add_section('rx')
        self._if_gain_config.set('rx', 'if_gain', str(None))
        self._if_gain_config.write(open(self.file_name, 'w'))
        self._freq_config = ConfigParser.ConfigParser()
        self._freq_config.read(self.file_name)
        if not self._freq_config.has_section('rx'):
        	self._freq_config.add_section('rx')
        self._freq_config.set('rx', 'rx_freq', str(None))
        self._freq_config.write(open(self.file_name, 'w'))
        self._bb_gain_config = ConfigParser.ConfigParser()
        self._bb_gain_config.read(self.file_name)
        if not self._bb_gain_config.has_section('rx'):
        	self._bb_gain_config.add_section('rx')
        self._bb_gain_config.set('rx', 'bb_gain', str(None))
        self._bb_gain_config.write(open(self.file_name, 'w'))
        self._wav_save_config = ConfigParser.ConfigParser()
        self._wav_save_config.read(self.file_name)
        if not self._wav_save_config.has_section('rx'):
        	self._wav_save_config.add_section('rx')
        self._wav_save_config.set('rx', 'rx_wav_file', str(None))
        self._wav_save_config.write(open(self.file_name, 'w'))

    def get_wav_save(self):
        return self.wav_save

    def set_wav_save(self, wav_save):
        self.wav_save = wav_save
        self.set_recfile(self.wav_save)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.set_xlate_filter_taps(firdes.low_pass(1, self.rf_samp_rate, 125000, 25000, firdes.WIN_HAMMING, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.rf_samp_rate)
        self.band_pass_filter.set_taps(firdes.complex_band_pass(1, self.rf_samp_rate, self.low, self.high, 500, firdes.WIN_HAMMING, 6.76))

    def get_xlate_filter_taps(self):
        return self.xlate_filter_taps

    def set_xlate_filter_taps(self, xlate_filter_taps):
        self.xlate_filter_taps = xlate_filter_taps
        self.freq_xlating_fir_filter_xxx_0.set_taps((self.xlate_filter_taps))

    def get_wav_samp_rate(self):
        return self.wav_samp_rate

    def set_wav_samp_rate(self, wav_samp_rate):
        self.wav_samp_rate = wav_samp_rate

    def get_rx_ppm(self):
        return self.rx_ppm

    def set_rx_ppm(self, rx_ppm):
        self.rx_ppm = rx_ppm
        self.osmosdr_source_0.set_freq_corr(self.rx_ppm, 0)

    def get_rx_dev(self):
        return self.rx_dev

    def set_rx_dev(self, rx_dev):
        self.rx_dev = rx_dev

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_source_0.set_gain(self.rf_gain, 0)

    def get_recfile(self):
        return self.recfile

    def set_recfile(self, recfile):
        self.recfile = recfile
        self.blocks_wavfile_sink_0.open(self.recfile)

    def get_prefix(self):
        return self.prefix

    def set_prefix(self, prefix):
        self.prefix = prefix

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.osmosdr_source_0.set_center_freq(self.freq-self.offset, 0)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.offset)

    def get_low(self):
        return self.low

    def set_low(self, low):
        self.low = low
        self.band_pass_filter.set_taps(firdes.complex_band_pass(1, self.rf_samp_rate, self.low, self.high, 500, firdes.WIN_HAMMING, 6.76))

    def get_if_samp_rate(self):
        return self.if_samp_rate

    def set_if_samp_rate(self, if_samp_rate):
        self.if_samp_rate = if_samp_rate

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_source_0.set_if_gain(self.if_gain, 0)

    def get_high(self):
        return self.high

    def set_high(self, high):
        self.high = high
        self.band_pass_filter.set_taps(firdes.complex_band_pass(1, self.rf_samp_rate, self.low, self.high, 500, firdes.WIN_HAMMING, 6.76))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq-self.offset, 0)

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_source_0.set_bb_gain(self.bb_gain, 0)

def check_time(cycle):
    now = time.localtime().tm_sec
    if cycle == 'odd':
        if now < 15:
            print("Waiting for 15 second mark...")
            time.sleep(14-now)
        elif now >= 45:
            print("Waiting for new minute...")
            time.sleep(61-now)
            check_time('odd')
        else:
            print("Waiting for 45 second mark...")
            time.sleep(44 - now)
    else:
        if now < 30:
            print("Waiting for 30 second mark")
            time.sleep(29-now)
        else:
            print("Waiting for the top of the minute...")
            time.sleep(59 - now)

def main(top_block_cls=ssb_rx_rec, options=None):

    tb = top_block_cls()
    check_time(cycle)
    print("\nReceiving...")
    tb.start()
    #time.sleep(15.2)
    #tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
