import pandas as pd
import numpy as np
import math


class HighToLowFactor(object):

    def __init__(self, stock_price_data, stock_price_calendar_tag,
                 set_num, holding_period):
        self.stock_price_data = stock_price_data
        self.stock_price_calendar_tag = stock_price_calendar_tag
        self.set_num = set_num
        self.holding_period = holding_period
        self.cur_high_to_low_factor = {}

    def calculate_high_to_low_factor(self, trade_time):
        if trade_time == 1:
            cur_day_data = self.stock_price_data[0:self.stock_price_calendar_tag[0]]
        else:
            cur_day_data = self.stock_price_data[self.stock_price_calendar_tag[trade_time - 2]:
                                                 self.stock_price_calendar_tag[trade_time - 1]]

        for line in cur_day_data:
            if line[-1] == '交易' and line[4] != line[5]:
                self.cur_high_to_low_factor[line[0]] = math.log(line[4]/line[5])