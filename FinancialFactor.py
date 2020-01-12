import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class FinancialFactor(object):

    def __init__(self, stock_price_data, stock_price_calendar_tag,
                 share_capital_data, share_capital_change_day,
                 share_income_data, share_income_day, share_income_report_day,
                 asset_data, debt_data, equity_data, balance_day,
                 set_num, holding_period):
        self.stock_price_data = stock_price_data
        self.stock_price_calendar_tag = stock_price_calendar_tag
        self.share_capital_data = share_capital_data
        self.share_capital_change_day = share_capital_change_day
        self.share_income_data = share_income_data
        self.share_income_day = share_income_day
        self.share_income_report_day = share_income_report_day
        self.cur_ep_factor = {}
        self.cur_divided_data = []
        self.set_num = set_num
        self.holding_period = holding_period
        self.last_divided_data = []
        self.stock_yield_answer = []
        self.cur_average_price = {}
        self.last_average_price = {}
        self.last_ep = {}
        self.asset_data = asset_data
        self.debt_data = debt_data
        self.equity_data = equity_data
        self.balance_day = balance_day
        self.bp_factor = {}
        self.roe_factor = {}
        self.leverage_factor = {}

    def calculate_ep(self, trade_time):
        self.last_ep = {}
        if trade_time == 1:
            cur_day_data = self.stock_price_data[0:self.stock_price_calendar_tag[0]]

        else:
            cur_day_data = self.stock_price_data[self.stock_price_calendar_tag[trade_time - 2]:
                                                 self.stock_price_calendar_tag[trade_time - 1]]

        for line in cur_day_data:  # did not consider special instance
            if line[0] in self.share_capital_change_day and line[0] in self.share_income_report_day:
                cur_share_capital_change_day = self.share_capital_change_day[line[0]]
                i = 0
                while (i < len(cur_share_capital_change_day) and
                       int(cur_share_capital_change_day[i]) < int(line[1])):
                    i += 1
                if (i < len(cur_share_capital_change_day) and
                        int(cur_share_capital_change_day[i]) == int(line[1])):
                    cur_capital_tag = i
                else:
                    cur_capital_tag = i - 1

                cur_share_income_report_day = self.share_income_report_day[line[0]]
                j = 0
                while (j < len(cur_share_income_report_day) and
                       int(cur_share_income_report_day[j]) < int(line[1])):
                    j += 1
                if (j < len(cur_share_income_report_day) and
                        int(cur_share_income_report_day[j]) == int(line[1])):
                    cur_income_tag = j
                else:
                    cur_income_tag = j - 1

                cur_balance_day = self.balance_day[line[0]]
                k = 0
                while (k < len(cur_balance_day) and
                       int(cur_balance_day[k]) < int(line[1])):
                    k += 1
                if (k < len(cur_balance_day) and
                        int(cur_balance_day[k]) == int(line[1])):
                    cur_balance_tag = k
                else:
                    cur_balance_tag = k - 1

                if cur_capital_tag >= 0 and cur_income_tag >= 0 and cur_balance_tag>=0 and (not np.isnan(line[6])):  # new data
                    self.last_ep[line[0]] = self.share_income_data[line[0]][cur_income_tag] / (
                            self.share_capital_data[line[0]][cur_capital_tag] * 10000) / line[6]
                    self.bp_factor[line[0]] = self.equity_data[line[0]][cur_balance_tag] / (
                            self.share_capital_data[line[0]][cur_capital_tag] * 10000) / line[6]
                    if self.equity_data[line[0]][cur_balance_tag] != 0:
                        self.roe_factor[line[0]] = self.share_income_data[line[0]][cur_income_tag] / self.equity_data[line[0]][cur_balance_tag]
                        self.leverage_factor[line[0]] = self.asset_data[line[0]][cur_balance_tag] / self.equity_data[line[0]][cur_balance_tag]
                    else:
                        self.roe_factor[line[0]] = self.share_income_data[line[0]][cur_income_tag] / 1
                        self.leverage_factor[line[0]] = self.asset_data[line[0]][cur_balance_tag] / 1

    def calculate_ep_factor(self, trade_time):
        self.cur_ep_factor = sorted(self.last_ep.items(), key=lambda kv: kv[1])
        # print(self.cur_ep_factor)
        self.cur_average_price = {}
        # self.last_ep = {}

        cur_day_data = self.stock_price_data[self.stock_price_calendar_tag[trade_time - 2]:
                                             self.stock_price_calendar_tag[trade_time - 1]]

        for line in cur_day_data:  # did not consider special instance
            # if line[0] in self.share_capital_change_day and line[0] in self.share_income_report_day:
            #     cur_share_capital_change_day = self.share_capital_change_day[line[0]]
            #     i = 0
            #     while (i < len(cur_share_capital_change_day) and
            #            int(cur_share_capital_change_day[i]) < int(line[1])):
            #         i += 1
            #     if (i < len(cur_share_capital_change_day) and
            #             int(cur_share_capital_change_day[i]) == int(line[1])):
            #         cur_capital_tag = i
            #     else:
            #         cur_capital_tag = i-1
            #
            #     cur_share_income_report_day = self.share_income_report_day[line[0]]
            #     j = 0
            #     while (j < len(cur_share_income_report_day) and
            #            int(cur_share_income_report_day[j]) < int(line[1])):
            #         j += 1
            #     if (j < len(cur_share_income_report_day) and
            #             int(cur_share_income_report_day[j]) == int(line[1])):
            #         cur_income_tag = j
            #     else:
            #         cur_income_tag = j - 1
            #
            #     if cur_capital_tag >= 0 and cur_income_tag >= 0:
            #         self.last_ep[line[0]] = self.share_income_data[line[0]][cur_income_tag] / (
            #                 self.share_capital_data[line[0]][cur_capital_tag] * 10000) / line[6]
            if line[-1] == '交易' and line[4] != line[5]:
                self.cur_average_price[line[0]] = line[10] * line[11]

    def divide_factor_data(self):  # divide factor data
        each_set_num = int(len(self.cur_ep_factor) / self.set_num)
        tail_num = len(self.cur_ep_factor) - self.set_num * each_set_num

        self.cur_divided_data = []
        start = 0
        for i in range(self.set_num):
            if tail_num > 0:
                end = (i + 1) * each_set_num + 1
            else:
                end = (i + 1) * each_set_num
            i -= 1
            self.cur_divided_data.append(self.cur_ep_factor[start:end])
            start = end
        # print(self.cur_divided_data)

    def trade(self, cur_trade_day):  # trade and calculate yield
        yield_answer = []
        if cur_trade_day >= 3:
            for stock_set in self.cur_divided_data:
                # print(len(self.last_divided_data))
                stock_set_yield = []
                for stock in stock_set:
                    if stock[0] in self.cur_average_price and stock[0] in self.last_average_price:
                        stock_set_yield.append(
                            (self.cur_average_price[stock[0]] - self.last_average_price[
                                stock[0]]) / self.last_average_price[stock[0]])
                    else:
                        stock_set_yield.append(0.0)  # did not resolve special instance
                yield_answer.append(np.mean(stock_set_yield))
            average_set = [i - np.mean(yield_answer) for i in yield_answer]
            self.stock_yield_answer.append(np.add(self.stock_yield_answer[-1], average_set))
        # self.last_divided_data = self.cur_divided_data

    def draw_answer(self):
        fig, ax = plt.subplots()
        x_num = (len(self.stock_price_calendar_tag) - 2) / self.holding_period + 1

        x = np.linspace(0, len(self.stock_price_calendar_tag), x_num)

        for i in range(self.set_num):
            ax.plot(x, np.asarray(self.stock_yield_answer)[:, i], label='Group' + str(i + 1) + 'Return')

        ax.legend()
        plt.xlabel('trade day number')
        plt.ylabel('rate of return')
        plt.show()

    def execute_factor(self):
        self.stock_yield_answer.append([0 for i in range(self.set_num)])

        trade_day = 2
        print(len(self.stock_price_calendar_tag))

        while trade_day <= len(self.stock_price_calendar_tag):
            print(trade_day)
            self.calculate_ep(trade_day-1)
            self.calculate_ep_factor(trade_day)
            self.divide_factor_data()
            self.last_average_price = self.cur_average_price
            trade_day += self.holding_period
            if trade_day <= len(self.stock_price_calendar_tag):
                self.calculate_ep_factor(trade_day)
                self.trade(trade_day)
            # self.divide_factor_data()

        pd.DataFrame(self.stock_yield_answer).to_csv('ep_result.csv')
        self.draw_answer()
