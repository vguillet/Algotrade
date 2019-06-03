"""
Prototype 1

This prototype is based entirely on technical analysis, and is ment as a test for the spline toolbox and RSI, SMA and OC
indicators

Victor Guillet
11/28/2018
"""

from PhyTrade.Technical_Analysis.Data_Collection_preparation.Big_Data import BIGDATA
from PhyTrade.Technical_Analysis.Data_Collection_preparation.Yahoo import pull_yahoo_data

from PhyTrade.Technical_Analysis.Indicators.RSI_gen import RSI
from PhyTrade.Technical_Analysis.Indicators.SMA_gen import SMA
from PhyTrade.Technical_Analysis.Amplification_signals.Volume_gen import VOLUME

from Twitter_Analysis.GetOldTwitterData.SentimentalAnalysis import polarity_over_time

from PhyTrade.Technical_Analysis.Tools.OC_tools import OC
from PhyTrade.Technical_Analysis.Tools.SPLINE_tools import SPLINE
from PhyTrade.Technical_Analysis.Tools.Major_spline_gen import MAJOR_SPLINE
from PhyTrade.Technical_Analysis.Tools.MATH_tools import MATH

import numpy as np
import pandas as pd
import datetime


class Prototype_1:
    def __init__(self):

        # ========================= DATA COLLECTION INITIALISATION =======================
        ticker = 'AAPL'                     # Ticker selected for Yahoo data collection
        data = pull_yahoo_data(ticker)      # Pull data from Yahoo

        # ------------------ Fill in missing values (weekends)
        idx = pd.date_range(data.index[0], data.index[-1])
        data = data.reindex(idx)
        data = data.fillna(method='ffill')

        data = data.reset_index()
        print(data)
        self.data = data
        # ========================= ANALYSIS INITIALISATION ==============================

        start_date = "2018-10-01"
        end_date = "2019-01-01"

        data_slice_start_ind = np.flatnonzero(data['index'] == start_date)[0]
        data_slice_stop_ind = np.flatnonzero(data['index'] == end_date)[0]
    
        self.big_data = BIGDATA(data, ticker, data_slice_start_ind, data_slice_stop_ind)
        # ------------------ Tools initialisation
        self.oc_tools = OC()
        self.spline_tools = SPLINE(self.big_data)

        # ------------------ Indicators initialisation
        setattr(self.big_data, "rsi", RSI(self.big_data, timeframe=14))
        setattr(self.big_data, "sma_1", SMA(self.big_data, timeperiod_1=10, timeperiod_2=25))
        setattr(self.big_data, "sma_2", SMA(self.big_data, timeperiod_1=5, timeperiod_2=15))
    
        setattr(self.big_data, "volume", VOLUME(self.big_data))

        # ================================================================================
        """
        
        
        
        
        
        
        
        
        """
        # ========================= DATA GENERATION AND PROCESSING =======================
        # ------------------ Indicators output generation
        self.big_data.rsi.get_output(self.big_data, include_triggers_in_bb_signal=True)
        self.big_data.sma_1.get_output(self.big_data, include_triggers_in_bb_signal=False)
        self.big_data.sma_2.get_output(self.big_data, include_triggers_in_bb_signal=False)

        # ------------------ Twitter analysis processing

        starting_date = datetime.date(2018, 11, 25)
        ending_date = datetime.date(2019, 1, 15)

        twitter_signal = polarity_over_time(starting_date, ending_date, toggle_plot=False)

        # ------------------ BB signals processing
        # -- Creating splines from signals
        setattr(self.big_data, "spline_rsi",
                self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.rsi.bb_signal, smoothing_factor=.3))
    
        setattr(self.big_data, "spline_oc_avg_gradient",
                self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.oc_avg_gradient_bb_signal, smoothing_factor=5))
    
        setattr(self.big_data, "spline_sma_1",
                self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.sma_1.bb_signal, smoothing_factor=1))
        setattr(self.big_data, "spline_sma_2",
                self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.sma_2.bb_signal, smoothing_factor=1))

        setattr(self.big_data, "spline_twitter_analysis",
                self.spline_tools.calc_signal_to_spline(self.big_data, twitter_signal,
                                                        smoothing_factor=0))

        self.big_data.spline_twitter_analysis = MATH.normalise_minus_one_one(self.big_data.spline_twitter_analysis)

        self.big_data.spline_twitter_analysis = SPLINE.flip_spline(self.big_data.spline_twitter_analysis)

        setattr(self.big_data, "spline_volume",
                self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.volume.amp_coef, smoothing_factor=0.5))
    
        # -- Adding signals together
        setattr(self.big_data, "combined_spline", self.spline_tools.combine_splines(self.big_data,
                                                                                    self.big_data.spline_rsi,
                                                                                    self.big_data.spline_oc_avg_gradient,
                                                                                    self.big_data.spline_sma_1,
                                                                                    self.big_data.spline_sma_2,
                                                                                    self.big_data.spline_twitter_analysis,
                                                                                    weight_1=0,
                                                                                    weight_2=0,
                                                                                    weight_3=0,
                                                                                    weight_4=0,
                                                                                    weight_5=1))

        # -- Tuning combined signal
        # self.big_data.combined_spline = \
        #     self.spline_tools.modulate_amplitude_spline(self.big_data.combined_spline, self.big_data.spline_volume)

        self.big_data.combined_spline = MATH().normalise_minus_one_one(self.big_data.combined_spline)

        # -- Creating dynamic thresholds
        upper_threshold, lower_threshold = \
            self.spline_tools.calc_thresholds(self.big_data, self.big_data.combined_spline,
                                              buffer=0.05, buffer_setting=0,
                                              standard_upper_threshold=0.5,
                                              standard_lower_threshold=-0.6)

        # ~~~~~~~~~~~~~~~~~~ Creating Major Spline/trigger values
        self.big_data.Major_spline = MAJOR_SPLINE(self.big_data, self.big_data.combined_spline,
                                                  upper_threshold, lower_threshold)
    # ================================================================================
    """








    """
    # ========================= SIGNAL PLOTS =========================================
    def plot(self, plot_1=True, plot_2=True, plot_3=True):

        import matplotlib.pyplot as plt

        # ---------------------------------------------- Plot 1
        if plot_1:
            # ------------------ Plot Open/Close prices
            ax1 = plt.subplot(211)
            self.oc_tools.plot_oc_values(self.big_data)
            # oc.plot_trigger_values(self.big_data)

            # ------------------ Plot RSI
            ax2 = plt.subplot(212, sharex=ax1)
            self.big_data.rsi.plot_rsi(self.big_data)
            plt.show()

        if plot_2:
            # ---------------------------------------------- Plot 2
            # ------------------ Plot Open/Close prices
            ax3 = plt.subplot(211)
            self.oc_tools.plot_oc_values(self.big_data)
            # oc.plot_trigger_values(self.big_data)

            # ------------------ Plot SMA Signal
            ax4 = plt.subplot(212, sharex=ax3)
            self.big_data.sma_1.plot_sma(self.big_data, plot_trigger_signals=False)
            plt.show()

        if plot_3:
            # ---------------------------------------------- Plot 3
            # ------------------ Plot Open/Close prices
            ax5 = plt.subplot(211)
            self.oc_tools.plot_oc_values(self.big_data)
            self.oc_tools.plot_trigger_values(
                self.big_data, self.big_data.Major_spline.sell_dates, self.big_data.Major_spline.buy_dates)

            # ------------------ Plot bb signal(s)
            ax6 = plt.subplot(212)
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_rsi, label="RSI bb spline")
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_oc_avg_gradient, label="OC gradient bb spline", color='m')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_sma_1, label="SMA_1 bb spline", color='r')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_sma_2, label="SMA_2 bb spline", color='b')

            self.spline_tools.plot_spline(
                self.big_data, self.big_data.spline_twitter_analysis, label="Twitter analysis", color='b')

            self.spline_tools.plot_spline(
                self.big_data, self.big_data.Major_spline.spline, label="Major spline", color='y')

            self.spline_tools. plot_spline(
                self.big_data, self.big_data.Major_spline.upper_threshold, label="Upper threshold")
            self.spline_tools. plot_spline(
                self.big_data, self.big_data.Major_spline.lower_threshold, label="Lower threshold")

            self.spline_tools.plot_spline_trigger(
                self.big_data, self.big_data.Major_spline.spline, self.big_data.Major_spline.sell_dates, self.big_data.Major_spline.buy_dates)

            # self.spline_tools.plot_spline(self.big_data, self.big_data.spline_volume, label="Volume", color='k')
            plt.show()
