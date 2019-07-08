<h2>Simple Automated FT8 Tool</h2>
<h3>Software Requirements:</h3>
This project depends on the gnuradio libraries as well as gr-osmosdr.<br>
https://github.com/gnuradio/gnuradio<br>
https://github.com/osmocom/gr-osmosdr
<br><br>
ft8encode and ft8decode were compiled from slightly modified wsjtx Fortran source code.<br>
https://sourceforge.net/p/wsjt/wsjtx/ci/master/tree/
<br><br>
<h3>Hardware Requirements:</h3>
You'll need one TX capable, osmosdr compatible SDR such as the BladeRF or HackRF.<br>
You'll also need an additional SDR as a receiver such as an RTL-SDR.<br>
<br>
Any values that you'll need to change can be found in ft8_qso.conf
<br>
<h4>A bit of a warning:</h4>
This program was built for testing purposes only and is not recommeded for use on the air.
