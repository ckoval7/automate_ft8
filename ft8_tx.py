#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: USB TX
# Author: K3CPK
# Description: USB transmitter using complex band pass filter.
# GNU Radio version: 3.7.13.5
##################################################

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
from datetime import datetime
import sys

try:
    cycle = sys.argv[1]
except:
    cycle = 'even'

class usb_tx_bpf(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "USB TX")

        ##################################################
        # Variables
        ##################################################
        self.low = low = 300
        self.filter_width = filter_width = 2.7e3
        self.file_name = file_name = "ft8_qso.conf"
        self._wav_samp_rate_config = ConfigParser.ConfigParser()
        self._wav_samp_rate_config.read(file_name)
        try: wav_samp_rate = self._wav_samp_rate_config.getfloat('tx', 'wav_samp_rate')
        except: wav_samp_rate = 12e3
        self.wav_samp_rate = wav_samp_rate
        self._wav_file_config = ConfigParser.ConfigParser()
        self._wav_file_config.read(file_name)
        try: wav_file = self._wav_file_config.get('tx', 'tx_wav_file')
        except: wav_file = './ft8_cq.wav'
        self.wav_file = wav_file
        self._tx_sdr_ppm_config = ConfigParser.ConfigParser()
        self._tx_sdr_ppm_config.read(file_name)
        try: tx_sdr_ppm = self._tx_sdr_ppm_config.getfloat('tx', 'tx_sdr_ppm')
        except: tx_sdr_ppm = 0
        self.tx_sdr_ppm = tx_sdr_ppm
        self._tx_freq_config = ConfigParser.ConfigParser()
        self._tx_freq_config.read(file_name)
        try: tx_freq = self._tx_freq_config.getfloat('tx', 'tx_freq')
        except: tx_freq = 144.174e6
        self.tx_freq = tx_freq
        self._tx_dev_string_config = ConfigParser.ConfigParser()
        self._tx_dev_string_config.read(file_name)
        try: tx_dev_string = self._tx_dev_string_config.get('tx', 'tx_device_string')
        except: tx_dev_string = 'hackrf=0'
        self.tx_dev_string = tx_dev_string
        self._rf_samp_rate_config = ConfigParser.ConfigParser()
        self._rf_samp_rate_config.read(file_name)
        try: rf_samp_rate = self._rf_samp_rate_config.getfloat('tx', 'rf_samp_rate')
        except: rf_samp_rate = 2e6
        self.rf_samp_rate = rf_samp_rate
        self._rf_gain_config = ConfigParser.ConfigParser()
        self._rf_gain_config.read(file_name)
        try: rf_gain = self._rf_gain_config.getfloat('tx', 'tx_rf_gain')
        except: rf_gain = 60
        print("RF Gain: " + str(rf_gain))
        self.rf_gain = rf_gain
        self._offset_config = ConfigParser.ConfigParser()
        self._offset_config.read(file_name)
        try: offset = self._offset_config.getfloat('tx', 'offset')
        except: offset = 5e3
        self.offset = offset
        self._if_samp_rate_config = ConfigParser.ConfigParser()
        self._if_samp_rate_config.read(file_name)
        try: if_samp_rate = self._if_samp_rate_config.getfloat('tx', 'if_samp_rate')
        except: if_samp_rate = 48e3
        self.if_samp_rate = if_samp_rate
        self._if_gain_config = ConfigParser.ConfigParser()
        self._if_gain_config.read(file_name)
        try: if_gain = self._if_gain_config.getfloat('tx', 'tx_if_gain')
        except: if_gain = 20
        self.if_gain = if_gain
        self.high = high = low+filter_width
        self._carrier_level_config = ConfigParser.ConfigParser()
        self._carrier_level_config.read(file_name)
        try: carrier_level = self._carrier_level_config.getfloat('tx', 'carrier_level')
        except: carrier_level = 1
        self.carrier_level = carrier_level
        self._bb_gain_config = ConfigParser.ConfigParser()
        self._bb_gain_config.read(file_name)
        try: bb_gain = self._bb_gain_config.getfloat('tx', 'tx_bb_gain')
        except: bb_gain = 20
        self.bb_gain = bb_gain
        self._audio_gain_config = ConfigParser.ConfigParser()
        self._audio_gain_config.read(file_name)
        try: audio_gain = self._audio_gain_config.getfloat('tx', 'audio_gain')
        except: audio_gain = 600e-3
        self.audio_gain = audio_gain

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=int(rf_samp_rate),
                decimation=int(if_samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=int(if_samp_rate),
                decimation=int(wav_samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + tx_dev_string )
        self.osmosdr_sink_0.set_sample_rate(rf_samp_rate)
        self.osmosdr_sink_0.set_center_freq(tx_freq-offset, 0)
        self.osmosdr_sink_0.set_freq_corr(tx_sdr_ppm, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.blocks_wavfile_source_0 = blocks.wavfile_source(wav_file, False)
        self.band_pass_filter_af = filter.fir_filter_fff(1, firdes.band_pass(
                1, wav_samp_rate, 300, 2700, 150, firdes.WIN_HAMMING, 6.76))
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((audio_gain, ))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.band_pass_filter_0 = filter.interp_fir_filter_ccc(1, firdes.complex_band_pass(
        	1, if_samp_rate, low, high, 100, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_0 = analog.sig_source_c(if_samp_rate, analog.GR_COS_WAVE, offset, 1, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(if_samp_rate, analog.GR_SIN_WAVE, 0, carrier_level, 0)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.band_pass_filter_af, 0))
        self.connect((self.band_pass_filter_af, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.osmosdr_sink_0, 0))

    def get_low(self):
        return self.low

    def set_low(self, low):
        self.low = low
        self.set_high(self.low+self.filter_width)
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, self.low, self.high, 100, firdes.WIN_HAMMING, 6.76))

    def get_filter_width(self):
        return self.filter_width

    def set_filter_width(self, filter_width):
        self.filter_width = filter_width
        self.set_high(self.low+self.filter_width)

    def get_file_name(self):
        return self.file_name

    def set_file_name(self, file_name):
        self.file_name = file_name
        self._wav_samp_rate_config = ConfigParser.ConfigParser()
        self._wav_samp_rate_config.read(self.file_name)
        if not self._wav_samp_rate_config.has_section('tx'):
        	self._wav_samp_rate_config.add_section('tx')
        self._wav_samp_rate_config.set('tx', 'wav_samp_rate', str(None))
        self._wav_samp_rate_config.write(open(self.file_name, 'w'))
        self._wav_file_config = ConfigParser.ConfigParser()
        self._wav_file_config.read(self.file_name)
        if not self._wav_file_config.has_section('tx'):
        	self._wav_file_config.add_section('tx')
        self._wav_file_config.set('tx', 'tx_wav_file', str(None))
        self._wav_file_config.write(open(self.file_name, 'w'))
        self._tx_sdr_ppm_config = ConfigParser.ConfigParser()
        self._tx_sdr_ppm_config.read(self.file_name)
        if not self._tx_sdr_ppm_config.has_section('tx'):
        	self._tx_sdr_ppm_config.add_section('tx')
        self._tx_sdr_ppm_config.set('tx', 'tx_sdr_ppm', str(None))
        self._tx_sdr_ppm_config.write(open(self.file_name, 'w'))
        self._tx_freq_config = ConfigParser.ConfigParser()
        self._tx_freq_config.read(self.file_name)
        if not self._tx_freq_config.has_section('tx'):
        	self._tx_freq_config.add_section('tx')
        self._tx_freq_config.set('tx', 'tx_freq', str(None))
        self._tx_freq_config.write(open(self.file_name, 'w'))
        self._tx_dev_string_config = ConfigParser.ConfigParser()
        self._tx_dev_string_config.read(self.file_name)
        if not self._tx_dev_string_config.has_section('tx'):
        	self._tx_dev_string_config.add_section('tx')
        self._tx_dev_string_config.set('tx', 'tx_device_string', str(None))
        self._tx_dev_string_config.write(open(self.file_name, 'w'))
        self._rf_samp_rate_config = ConfigParser.ConfigParser()
        self._rf_samp_rate_config.read(self.file_name)
        if not self._rf_samp_rate_config.has_section('tx'):
        	self._rf_samp_rate_config.add_section('tx')
        self._rf_samp_rate_config.set('tx', 'rf_samp_rate', str(None))
        self._rf_samp_rate_config.write(open(self.file_name, 'w'))
        self._rf_gain_config = ConfigParser.ConfigParser()
        self._rf_gain_config.read(self.file_name)
        if not self._rf_gain_config.has_section('tx'):
        	self._rf_gain_config.add_section('tx')
        self._rf_gain_config.set('tx', 'tx_rf_gain', str(None))
        self._rf_gain_config.write(open(self.file_name, 'w'))
        self._offset_config = ConfigParser.ConfigParser()
        self._offset_config.read(self.file_name)
        if not self._offset_config.has_section('tx'):
        	self._offset_config.add_section('tx')
        self._offset_config.set('tx', 'offset', str(None))
        self._offset_config.write(open(self.file_name, 'w'))
        self._if_samp_rate_config = ConfigParser.ConfigParser()
        self._if_samp_rate_config.read(self.file_name)
        if not self._if_samp_rate_config.has_section('tx'):
        	self._if_samp_rate_config.add_section('tx')
        self._if_samp_rate_config.set('tx', 'if_samp_rate', str(None))
        self._if_samp_rate_config.write(open(self.file_name, 'w'))
        self._if_gain_config = ConfigParser.ConfigParser()
        self._if_gain_config.read(self.file_name)
        if not self._if_gain_config.has_section('tx'):
        	self._if_gain_config.add_section('tx')
        self._if_gain_config.set('tx', 'tx_if_gain', str(None))
        self._if_gain_config.write(open(self.file_name, 'w'))
        self._carrier_level_config = ConfigParser.ConfigParser()
        self._carrier_level_config.read(self.file_name)
        if not self._carrier_level_config.has_section('tx'):
        	self._carrier_level_config.add_section('tx')
        self._carrier_level_config.set('tx', 'carrier_level', str(None))
        self._carrier_level_config.write(open(self.file_name, 'w'))
        self._bb_gain_config = ConfigParser.ConfigParser()
        self._bb_gain_config.read(self.file_name)
        if not self._bb_gain_config.has_section('tx'):
        	self._bb_gain_config.add_section('tx')
        self._bb_gain_config.set('tx', 'tx_bb_gain', str(None))
        self._bb_gain_config.write(open(self.file_name, 'w'))
        self._audio_gain_config = ConfigParser.ConfigParser()
        self._audio_gain_config.read(self.file_name)
        if not self._audio_gain_config.has_section('tx'):
        	self._audio_gain_config.add_section('tx')
        self._audio_gain_config.set('tx', 'audio_gain', str(None))
        self._audio_gain_config.write(open(self.file_name, 'w'))

    def get_wav_samp_rate(self):
        return self.wav_samp_rate

    def set_wav_samp_rate(self, wav_samp_rate):
        self.wav_samp_rate = wav_samp_rate

    def get_wav_file(self):
        return self.wav_file

    def set_wav_file(self, wav_file):
        self.wav_file = wav_file

    def get_tx_sdr_ppm(self):
        return self.tx_sdr_ppm

    def set_tx_sdr_ppm(self, tx_sdr_ppm):
        self.tx_sdr_ppm = tx_sdr_ppm
        self.osmosdr_sink_0.set_freq_corr(self.tx_sdr_ppm, 0)

    def get_tx_freq(self):
        return self.tx_freq

    def set_tx_freq(self, tx_freq):
        self.tx_freq = tx_freq
        self.osmosdr_sink_0.set_center_freq(self.tx_freq-self.offset, 0)

    def get_tx_dev_string(self):
        return self.tx_dev_string

    def set_tx_dev_string(self, tx_dev_string):
        self.tx_dev_string = tx_dev_string

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.rf_samp_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.osmosdr_sink_0.set_center_freq(self.tx_freq-self.offset, 0)
        self.analog_sig_source_x_0_0.set_frequency(self.offset)

    def get_if_samp_rate(self):
        return self.if_samp_rate

    def set_if_samp_rate(self, if_samp_rate):
        self.if_samp_rate = if_samp_rate
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, self.low, self.high, 100, firdes.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_0.set_sampling_freq(self.if_samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.if_samp_rate)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_high(self):
        return self.high

    def set_high(self, high):
        self.high = high
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, self.low, self.high, 100, firdes.WIN_HAMMING, 6.76))

    def get_carrier_level(self):
        return self.carrier_level

    def set_carrier_level(self, carrier_level):
        self.carrier_level = carrier_level
        self.analog_sig_source_x_0.set_amplitude(self.carrier_level)

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_sink_0.set_bb_gain(self.bb_gain, 0)

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0.set_k((self.audio_gain, ))

def check_time(cycle):
    #now = time.localtime().tm_sec
    now = float(datetime.now().strftime('%S.%f'))
    if cycle == 'odd':
        if now < 15:
            print("Waiting for 15 second mark...")
            time.sleep(15-now)
        elif now >= 45:
            print("Waiting for new minute...")
            time.sleep(61-now)
            check_time('odd')
        else:
            print("Waiting for 45 second mark...")
            time.sleep(45 - now)
    else:
        if now < 30:
            print("Waiting for 30 second mark")
            time.sleep((30-0.4)-now)
        else:
            print("Waiting for the top of the minute...")
            time.sleep((60-0.4) - now)

def main(top_block_cls=usb_tx_bpf, options=None):

    tb = top_block_cls()
    check_time(cycle)
    print("\nTransmitting...")
    tb.start()
    tb.wait()
    tb.stop()

if __name__ == '__main__':
    main()
