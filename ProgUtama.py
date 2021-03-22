                                             # Tugas Akhir Tahun 2020 #
# Judul TA  : Perancangan dan Realisasi Sistem Pemantauan Spektrum Frekuensi Radio
#             pada Pita VHF dan UHF Berbasis Teknologi SDR untuk Wilayah Bandung
# Nama      : Angga Maulana
# NIM       : 171331005
# Kelas     : 3A
# Prodi     : Teknik Telekomunikasi
# Jurusan   : Teknik Elektro
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from gnuradio import qtgui
from PyQt5 import *
from PyQt5.QtGui import *
from datetime import *
from gnuradio import eng_notation
from gnuradio.eng_arg import eng_float, intx
from argparse import ArgumentParser
from gnuradio import analog
from gnuradio import audio
from gnuradio import filter
from gnuradio import gr
from gnuradio import blocks
import sip
import sys
import signal
import time
import osmosdr
import mysql.connector

class TA2020(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Sistem Pemantauan Spektrum Frekuensi Radio")

        Qt.QWidget.__init__(self)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "TA2020")


        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 0
        self.samp_rate = samp_rate = 2e6
        self.TunerFC = TunerFC = 80e6
        self.down_rate = down_rate = 250e3
        self.rfgain = rfgain = 0
        self.ifgain = ifgain = 0
        self.bbgain = bbgain = 0


    ##################################################
    # QT GUI Range
    ##################################################
        self._TunerFC_range = Range(80e6, 850e6, 1, 80e6, 200)
        self._TunerFC_win = RangeWidget(self._TunerFC_range, self.set_TunerFC, 'Tuner FC', "counter_slider", float)
        self.top_grid_layout.addWidget(self._TunerFC_win, 2,1,1,7)

        ##############################################
        #Gain
        ##############################################
        self._rfgain_range = Range(0, 60, 1, 0, 200)
        self._rfgain_win = RangeWidget(self._rfgain_range, self.set_rfgain, 'RF Gain', "counter", float)
        self.top_grid_layout.addWidget(self._rfgain_win, 3, 1, 1, 3)

        self._ifgain_range = Range(0, 60, 1, 0, 200)
        self._ifgain_win = RangeWidget(self._ifgain_range, self.set_ifgain, 'IF Gain', "counter", float)
        self.top_grid_layout.addWidget(self._ifgain_win, 4, 1, 1, 3)

        self._bbgain_range = Range(0, 60, 1, 0, 200)
        self._bbgain_win = RangeWidget(self._bbgain_range, self.set_bbgain, 'BB Gain', "counter", float)
        self.top_grid_layout.addWidget(self._bbgain_win, 5, 1, 1, 3)

        self._volume_range = Range(0, 100, 1, 0, 50)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "slider", float)
        self.top_grid_layout.addWidget(self._volume_win, 6, 1, 1, 3)


    ############################################################
    #Frame Style
    ############################################################
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(114, 159, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(196, 225, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(155, 192, 231))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(57, 79, 103))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(76, 106, 138))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(184, 207, 231))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(114, 159, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(196, 225, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(155, 192, 231))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(57, 79, 103))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(76, 106, 138))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(184, 207, 231))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(57, 79, 103))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(114, 159, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(196, 225, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(155, 192, 231))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(57, 79, 103))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(76, 106, 138))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(57, 79, 103))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(57, 79, 103))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(114, 159, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(114, 159, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)

        self.top_widget.setPalette(palette)


    ############################################################
    #Frame Mencari Range Frekuensi
    ############################################################

        self.frame = QFrame(self.top_widget)
        self.frame.setPalette(palette)
        self.frame.setLineWidth(5)
        self.frame.setFixedSize(480,33)
        self.top_grid_layout.addWidget(self.frame, 2,8,1,2)

        self.label1 = QLabel(self.frame)
        self.label1.setText("Frekuensi :")
        font = QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(17)
        font.setWeight(75)
        self.label1.setFont(font)
        self.label1.move(0, 1)

        self.editbx = QTextEdit(self.frame)
        self.editbx.setGeometry(100, 3, 80, 27)

        self.label2 = QLabel(self.frame)
        self.label2.setText(" ~ ")
        self.label2.move(190,5)

        self.editbx2 = QTextEdit(self.frame)
        self.editbx2.setGeometry(216, 3, 80, 27)

        self.pb = QPushButton(self.frame)
        self.pb.setText("Cari")
        self.pb.setGeometry(370, 3, 80, 27)

        self.label3 = QLabel(self.frame)
        self.label3.setText("MHz")
        self.label3.setFont(font)
        self.label3.move(308, 4)

        self.pb.clicked.connect(self.clicked)


    ######################################################################
    #Frame Database
    ######################################################################
        #######################################################
        #Database FM
        #######################################################
        self.frame2 = QFrame(self.top_widget)
        self.frame2.setPalette(palette)
        self.frame2.setFixedSize(800, 244)
        self.top_grid_layout.addWidget(self.frame2, 3, 4, 4, 3)

        self.label4 = QLabel(self.frame2)
        self.label4.setText("Daftar Okupansi FM :")
        font2 = QFont()
        font2.setPointSize(13)
        self.label4.setFont(font2)
        self.label4.move(0,5)

        self.listWidget = QListWidget(self.frame2)
        self.listWidget.setFont(font2)
        self.listWidget.setGeometry(0,30,350,214)


        ###########################################################
        #Database TV
        ###########################################################
        self.frame3 = QFrame(self.frame2)
        self.frame3.setPalette(palette)
        self.frame3.setLineWidth(5)
        self.frame3.setFixedSize(320, 244)
        self.frame3.setGeometry(400,0,600,280)

        self.label5 = QLabel(self.frame3)
        self.label5.setText("Daftar Okupansi TV :")
        self.label5.setFont(font2)
        self.label5.move(0, 5)

        self.listWidget2 = QListWidget(self.frame3)
        font5 = QFont()
        font5.setPointSize(14)
        self.listWidget2.setFont(font5)
        self.listWidget2.setGeometry(0, 30, 140, 214)

        ##############################################
        #buton generate
        ##############################################

        self.butonfm = QPushButton(self.frame3)
        self.butonfm.setText("Generate FM")
        self.butonfm.setGeometry(180, 50, 100, 27)
        self.butonfm.clicked.connect(self.clickedfm)
        
        self.butontv = QPushButton(self.frame3)
        self.butontv.setText("Generate TV")
        self.butontv.setGeometry(180, 110, 100, 27)
        self.butontv.clicked.connect(self.clickedtv)


        #########################################################################
        #Event logs
        #########################################################################
        self.frame4 = QFrame(self.top_widget)
        self.frame4.setPalette(palette)
        self.frame4.setLineWidth(10)
        self.frame4.setFixedSize(600, 244)
        self.top_grid_layout.addWidget(self.frame4, 3, 7, 4, 3)

        self.label6 = QLabel(self.frame4)
        self.label6.setText("History :")
        font4 = QFont()
        font4.setPointSize(12)
        self.label6.setFont(font4)
        self.label6.move(0, 0)

        self.Eventwid = QTextEdit(self.frame4)
        self.Eventwid.setReadOnly(True)
        self.Eventwid.setFixedSize(600,214)
        font5 = QFont()
        font5.setPointSize(10)
        font5.setFamily("Chiller")
        self.Eventwid.setFont(font5)
        self.Eventwid.setAcceptDrops(True)
        self.Eventwid.setGeometry(0,29,0,0)


        ##########################################################################
        #RTL-SDR
        ##########################################################################
        self.rtlsdr = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.rtlsdr.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr.set_sample_rate(samp_rate)
        self.rtlsdr.set_center_freq(self.TunerFC, 0)
        self.rtlsdr.set_freq_corr(0, 0)
        self.rtlsdr.set_gain(self.rfgain, 0)
        self.rtlsdr.set_if_gain(self.ifgain, 0)
        self.rtlsdr.set_bb_gain(self.bbgain, 0)
        self.rtlsdr.set_antenna('', 0)
        self.rtlsdr.set_bandwidth(0, 0)
        
        
        self.ratresampler = filter.rational_resampler_fff(
            interpolation=24,
            decimation=250,
            taps=None,
            fractional_bw=None)
        
        
        self.qtguigraph = qtgui.freq_sink_c(
            1024,  # size
            firdes.WIN_BLACKMAN_hARRIS,  # wintype
            self.TunerFC,  # fc
            samp_rate,  # bw
            "",  # name
            1
        )
        self.qtguigraph.set_update_time(0.10)
        self.qtguigraph.set_y_axis(-140, 10)
        self.qtguigraph.set_y_label('Amplitude', 'dBm')
        self.qtguigraph.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtguigraph.enable_autoscale(False)
        self.qtguigraph.enable_grid(True)
        self.qtguigraph.set_fft_average(0.3)
        self.qtguigraph.enable_axis_labels(True)
        self.qtguigraph.enable_control_panel(True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            self.qtguigraph.set_line_label(i, labels[i])
            self.qtguigraph.set_line_width(i, widths[i])
            self.qtguigraph.set_line_color(i, colors[i])
            self.qtguigraph.set_line_alpha(i, alphas[i])

        self._qtguigraph_win = sip.wrapinstance(self.qtguigraph.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtguigraph_win, 1, 1, 1, 9)

        self.lpf = filter.fir_filter_ccf(
            int(samp_rate / down_rate),
            firdes.low_pass(
                2,
                samp_rate,
                100e3,
                10e3,
                firdes.WIN_KAISER,
                6.76))
        self.multiplyconst = blocks.multiply_const_ff(volume/100)
        self.audiosink = audio.sink(24000, '', True)
        self.analogwfm = analog.wfm_rcv(
            quad_rate=down_rate,
            audio_decimation=1,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analogwfm, 0), (self.ratresampler, 0))
        self.connect((self.multiplyconst, 0), (self.audiosink, 0))
        self.connect((self.lpf, 0), (self.analogwfm, 0))
        self.connect((self.ratresampler, 0), (self.multiplyconst, 0))
        self.connect((self.rtlsdr, 0), (self.lpf, 0))
        self.connect((self.rtlsdr, 0), (self.qtguigraph, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "TA2020")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


    def clicked(self):
        self.startfrek = self.editbx.toPlainText()
        self.stopfrek = self.editbx2.toPlainText()
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database="TA2020",
            auth_plugin="mysql_native_password"
        )

        self.mycursor = mydb.cursor()
        self.mycursor.execute("SELECT okupansi FROM daftarfm WHERE frekuensi BETWEEN "
                              +str(self.startfrek)+" AND "+str(self.stopfrek))
        self.listWidget.clear()
        for db in self.mycursor:
            self.datafm = db
            self.listWidget.addItems(self.datafm)

        self.mycursor2 = mydb.cursor()
        self.mycursor2.execute("SELECT okupansi FROM daftartv WHERE frekuensi BETWEEN "
                               +str(self.startfrek)+" AND "+str(self.stopfrek))
        self.listWidget2.clear()
        for db2 in self.mycursor2:
            self.datatv = db2
            self.listWidget2.addItems(self.datatv)


    def clickedfm(self, TunerFC):
        self.datafrekfm = self.listWidget.selectedItems()
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database="TA2020",
            auth_plugin="mysql_native_password"
        )
        self.mycursor = mydb.cursor()
        for yy in self.datafrekfm:
            self.datafmok = yy.text()
        self.mycursor.execute("SELECT frekuensi FROM daftarfm WHERE okupansi = "
                              +"'"+str(self.datafmok)+"'")
        for db3 in self.mycursor:
            self.TunerFC = db3

        TunerFC = self.TunerFC
        str(self.TunerFC[0])
        self.TunerFC = self.TunerFC[0]
        now = datetime.now()
        dt_string = now.strftime("%B %d, %Y %H:%M:%S")

        self.Eventwid.insertPlainText(dt_string + " - Memantau " + str(self.datafmok) +
                                          " Pada Frekuensi " + str(self.TunerFC) + " MHz\n")
        self.curtext = QTextCursor(self.Eventwid.document())
        self.Eventwid.moveCursor(QTextCursor.End)
        self.TunerFC = float(self.TunerFC) * float(1000000)


        self.qtguigraph.set_frequency_range(float(self.TunerFC), self.samp_rate)
        self.rtlsdr.set_center_freq(self.TunerFC, 0)


        self.listWidget.clearSelection()
        self.datafrekfm.clear()

    def clickedtv(self):
        self.datafrektv = self.listWidget2.selectedItems()
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database="TA2020",
            auth_plugin="mysql_native_password"
        )
        self.mycursor = mydb.cursor()
        for xx in self.datafrektv:
            self.datatvok= xx.text()

        self.mycursor.execute("SELECT frekuensi FROM daftartv WHERE okupansi = "
                              "" + "'" + str(self.datatvok) + "'")
        for db34 in self.mycursor:
            self.TunerFC = db34
        TunerFC = self.TunerFC
        str(self.TunerFC[0])
        self.TunerFC = self.TunerFC[0]
        now = datetime.now()
        dt_string = now.strftime("%B %d, %Y %H:%M:%S")
        self.Eventwid.insertPlainText(dt_string + " - Memantau " + str(self.datatvok) +
                                      " Pada Frekuensi " + str(self.TunerFC) + " MHz\n")
        self.curtext = QTextCursor(self.Eventwid.document())
        self.Eventwid.moveCursor(QTextCursor.End)
        self.TunerFC = float(self.TunerFC) * float(1000000)

        self.qtguigraph.set_frequency_range(float(self.TunerFC), self.samp_rate)
        self.rtlsdr.set_center_freq(self.TunerFC, 0)

        self.listWidget2.clearSelection()
        self.datafrektv.clear()


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtguigraph.set_frequency_range(self.TunerFC, self.samp_rate)
        self.rtlsdr.set_sample_rate(self.samp_rate)
        self.lpf.set_taps(firdes.low_pass(2, self.samp_rate, 100e3, 10e3,
                                          firdes.WIN_KAISER, 6.76))


    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.multiplyconst.set_k(self.volume/100)

    def get_TunerFC(self):
        return self.TunerFC

    def set_TunerFC(self, TunerFC):
        self.TunerFC = TunerFC
        self.qtguigraph.set_frequency_range(self.TunerFC, self.samp_rate)
        self.rtlsdr.set_center_freq(self.TunerFC, 0)

    def get_down_rate(self):
        return self.down_rate

    def set_down_rate(self, down_rate):
        self.down_rate = down_rate

    def get_bbgain(self):
        return self.bbgain

    def set_bbgain(self, bbgain):
        self.bbgain = bbgain
        self.rtlsdr.set_bb_gain(self.bbgain, 0)

    def get_rfgain(self):
        return self.rfgain

    def set_rfgain(self, rfgain):
        self.rfgain = rfgain
        self.rtlsdr.set_gain(self.rfgain, 0)

    def get_ifgain(self):
        return self.ifgain

    def set_ifgain(self, ifgain):
        self.ifgain = ifgain
        self.rtlsdr.set_if_gain(self.ifgain, 0)


def main(top_block_cls=TA2020, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()