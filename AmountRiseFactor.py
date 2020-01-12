import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class AmountRiseFactor(object):

    def __init__(self, stock_price_data, stock_price_calendar_tag,
                 set_num, holding_period):
        self.stock_price_data = stock_price_data
        self.stock_price_calendar_tag = stock_price_calendar_tag
        self.cur_original_amount_rise_factor = {}
        self.cur_amount_rise_factor = {}
        self.cur_divided_data = []
        self.set_num = set_num
        self.holding_period = holding_period
        self.stock_yield_answer = []
        self.cur_average_price = {}
        self.last_average_price = {}
        self.last_amount = {}
        self.second_last_amount = {}

    def calculate_second_last_amount(self, trade_time):
        self.second_last_amount = {}

        if trade_time == 1:
            cur_day_data = self.stock_price_data[0:self.stock_price_calendar_tag[0]]
        else:
            cur_day_data = self.stock_price_data[self.stock_price_calendar_tag[trade_time - 2]:
                                                 self.stock_price_calendar_tag[trade_time - 1]]

        for line in cur_day_data:
            if line[-1] == '交易':
                # self.second_last_amount[line[0]] = line[8]   # old data
                self.second_last_amount[line[0]] = line[10]

    def calculate_daily_rise_factor(self, trade_time):
        self.cur_original_amount_rise_factor = {}
        self.cur_average_price = {}
        self.last_amount = {}

        if trade_time == 1:
            cur_day_data = self.stock_price_data[0:self.stock_price_calendar_tag[0]]
        else:
            cur_day_data = self.stock_price_data[self.stock_price_calendar_tag[trade_time - 2]:
                                                 self.stock_price_calendar_tag[trade_time - 1]]

        for line in cur_day_data:
            if line[-1] == '交易':
                # self.last_amount[line[0]] = line[8]
                self.last_amount[line[0]] = line[10]  # new data

        for line in cur_day_data:
            if line[-1] == '交易' and line[4] != line[5]:
                # self.cur_average_price[line[0]] = line[10] * line[11]
                self.cur_average_price[line[0]] = line[17] * line[16]  # new data
                if line[0] in self.last_amount and line[0] in self.second_last_amount:
                    self.cur_original_amount_rise_factor[line[0]] = (self.last_amount[line[0]] -
                                                                     self.second_last_amount[line[0]]) \
                                                                    / self.second_last_amount[line[0]]
        self.cur_amount_rise_factor = sorted(self.cur_original_amount_rise_factor.items(), key=lambda kv: kv[1])

    def divide_factor_data(self):  # divide factor data
        each_set_num = int(len(self.cur_amount_rise_factor) / self.set_num)
        tail_num = len(self.cur_amount_rise_factor) - self.set_num * each_set_num

        self.cur_divided_data = []
        start = 0
        for i in range(self.set_num):
            if tail_num > 0:
                end = (i + 1) * each_set_num + 1
            else:
                end = (i + 1) * each_set_num
            i -= 1
            self.cur_divided_data.append(self.cur_amount_rise_factor[start:end])
            start = end

    def trade(self, cur_trade_day):  # trade and calculate yield
        yield_answer = []
        for stock_set in self.cur_divided_data:
            # print(len(self.last_divided_data))
            stock_set_yield = []
            for stock in stock_set:
                if stock[0] in self.cur_average_price and stock[0] in self.last_average_price:
                    stock_set_yield.append(
                        (self.cur_average_price[stock[0]] - self.last_average_price[stock[0]])
                        / self.last_average_price[stock[0]])
                else:
                    stock_set_yield.append(0.0)  # did not resolve special instance
            yield_answer.append(np.mean(stock_set_yield))
        average_set = [i - np.mean(yield_answer) for i in yield_answer]
        self.stock_yield_answer.append(np.add(self.stock_yield_answer[-1], average_set))

    def draw_answer(self):
        fig, ax = plt.subplots()
        x_num = (len(self.stock_price_calendar_tag) - 3) / self.holding_period + 1

        x = np.linspace(0, len(self.stock_price_calendar_tag), x_num)

        for i in range(self.set_num):
            ax.plot(x, np.asarray(self.stock_yield_answer)[:, i], label='Group' + str(i + 1) + 'Return')

        ax.legend()
        plt.xlabel('trade day number')
        plt.ylabel('rate of return')
        plt.show()

    def execute_factor(self):
        self.stock_yield_answer.append([0 for i in range(self.set_num)])

        trade_day = 3
        while trade_day < len(self.stock_price_calendar_tag):
            print(trade_day)
            self.calculate_second_last_amount(trade_day-2)
            self.calculate_daily_rise_factor(trade_day-1)
            self.divide_factor_data()
            self.calculate_daily_rise_factor(trade_day)
            self.last_average_price = self.cur_average_price
            trade_day += self.holding_period
            if trade_day <= len(self.stock_price_calendar_tag):
                self.calculate_daily_rise_factor(trade_day)
                self.trade(trade_day)

        # print(np.asarray(self.stock_yield_answer))

        pd.DataFrame(self.stock_yield_answer).to_csv('amount_rise_result.csv')
        self.draw_answer()
