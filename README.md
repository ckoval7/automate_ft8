<h2>Simple Automated FT8 Tool</h2>
<h3>Software Requirements:</h3>
This project depends on the gnuradio libraries, libgfortran, as well as gr-osmosdr.<br>
https://github.com/gnuradio/gnuradio<br>
https://github.com/osmocom/gr-osmosdr
<br><br>
ft8encode and ft8decode were compiled from slightly modified wsjtx Fortran source code.<br>
https://sourceforge.net/p/wsjt/wsjtx/ci/master/tree/
<br><br>
For best results, please make sure your computer is synced with an accurate NTP server.
<h3>Hardware Requirements:</h3>
You'll need one TX capable, osmosdr compatible SDR such as the BladeRF or HackRF.<br>
You'll also need an additional SDR as a receiver such as an RTL-SDR.<br>
<br><br>
<h3>Usage</h3>
<ol>
   <li>Add your callsign and Maidenhead 4 character grid square to ft8_qso.conf</li>
   <li>Select even (:00/:30) or odd (:15/45) TX and RX cycles. If you are responding to a CQ, make sure the cycles are appropriate for the station calling.</li>
   <li>Set your TX and RX SDR gain and ppm values in ft8_qso.conf</li>
</ol>
<ul>
   <li>If you are calling CQ start<br>
   <code>python run_cq.py</code>.</li>
   <li>If you are resonding to a CQ, start<br>
   <code>python run_response.py</code></li>
</ul>
<br><br>
If you are receiving the other station with decent signal strength, but you are not decoding anything then check your NTP sync status and make sure your system time with within 500mS of UTC.
<br><br>
Any values that you'll need to change on the DSP side of things can be found in ft8_qso.conf<br>
<br>
<h4>A bit of a warning:</h4>
This program was built for testing purposes only and is not recommeded for use on the air.
