import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

class MaketValueFactor(object):

    def __init__(self, stock_price_data, stock_price_calendar_tag,
                 share_capital_data, share_capital_change_day, set_num, holding_period):
        self.stock_price_data = stock_price_data
        self.stock_price_calendar_tag = stock_price_calendar_tag
        self.share_capital_Data = share_capital_data
        self.share_capital_change_day = share_capital_change_day
        self.cur_original_market_value_factor = {}
        self.cur_market_value_factor = {}
        self.cur_divided_data = []
        self.set_num = set_num
        self.holding_period = holding_period
        self.last_market_value_factor = {}
        self.last_divided_data = []
        self.stock_yield_answer = []
        self.cur_average_market_value = {}
        self.last_average_market_value = {}
        self.non_linear_market_value = {}

    def calculate_market_value_factor(self, trade_time):
        self.cur_original_market_value_factor = {}
        self.cur_average_market_value = {}

        if trade_time == 1:
            cur_day_data = self.stock_price_data[0:self.stock_price_calendar_tag[trade_time - 1]]
        else:
            cur_day_data = self.stock_price_data[self.stock_price_calendar_tag[trade_time - 2]:
                                                 self.stock_price_calendar_tag[trade_time - 1]]

        for line in cur_day_data:  # did not consider special instance
            if line[0] in self.share_capital_change_day:
                cur_share_capital_change_day = self.share_capital_change_day[line[0]]
                i = 0
                while (i < len(cur_share_capital_change_day) and
                       int(cur_share_capital_change_day[i]) < int(line[1])):
                    i += 1
                if (i < len(cur_share_capital_change_day) and
                        int(cur_share_capital_change_day[i]) == int(line[1])):
                    cur_capital_tag = i
                else:
                    cur_capital_tag = i-1
                last_capital_tag = i-1

                self.cur_original_market_value_factor[line[0]] = line[2] * self.share_capital_Data[line[0]][
                    last_capital_tag] * 10000
                self.non_linear_market_value[line[0]] = math.log(line[2] * self.share_capital_Data[line[0]][
                    last_capital_tag] * 10000)
                self.cur_average_market_value[line[0]] = line[10] * self.share_capital_Data[line[0]][
                    cur_capital_tag] * 10000
        self.cur_market_value_factor = sorted(self.cur_original_market_value_factor.items(), key=lambda kv: kv[1])
        # print(self.cur_original_market_value_factor)

    def divide_factor_data(self):  # divide factor data
        each_set_num = int(len(self.cur_market_value_factor) / self.set_num)
        tail_num = len(self.cur_market_value_factor) - self.set_num * each_set_num

        self.cur_divided_data = []
        start = 0
        for i in range(self.set_num):
            if tail_num > 0:
                end = (i + 1) * each_set_num + 1
            else:
                end = (i + 1) * each_set_num
            i -= 1
            self.cur_divided_data.append(self.cur_market_value_factor[start:end])
            start = end

    def trade(self, cur_trade_day):  # trade and calculate yield
        yield_answer = []
        if cur_trade_day != 1:
            for stock_set in self.last_divided_data:
                # print(len(self.last_divided_data))
                stock_set_yield = []
                for stock in stock_set:
                    if stock[0] in self.cur_average_market_value:
                        stock_set_yield.append((self.cur_average_market_value[stock[0]] - self.last_average_market_value[
                            stock[0]]) / self.last_average_market_value[stock[0]])
                    else:
                        stock_set_yield.append(0.0)
                yield_answer.append(np.mean(stock_set_yield))
            average_set = [i - np.mean(yield_answer) for i in yield_answer]
            self.stock_yield_answer.append(np.add(self.stock_yield_answer[-1], average_set))

        self.last_market_value_factor = self.cur_market_value_factor
        self.last_divided_data = self.cur_divided_data
        self.last_average_market_value = self.cur_average_market_value

    def draw_answer(self):
        fig, ax = plt.subplots()
        x_num = (len(self.stock_price_calendar_tag) - 1) / self.holding_period + 1

        x = np.linspace(0, len(self.stock_price_calendar_tag), x_num)

        for i in range(self.set_num):
            ax.plot(x, np.asarray(self.stock_yield_answer)[:, i], label='Group' + str(i + 1) + 'Return')

        ax.legend()
        plt.xlabel('trade day number')
        plt.ylabel('rate of return')
        plt.show()

    def execute_factor(self):
        self.stock_yield_answer.append([0 for i in range(self.set_num)])

        trade_day = 1
        while trade_day <= len(self.stock_price_calendar_tag):
            print(trade_day)
            self.calculate_market_value_factor(trade_day)
            self.divide_factor_data()
            self.trade(trade_day)
            trade_day += self.holding_period

        pd.DataFrame(self.stock_yield_answer).to_csv('market_value_result.csv')
        self.draw_answer()