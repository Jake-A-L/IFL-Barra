import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
# import IndustryResolver


class OriginalDataWasher(object):

    def __init__(self, industry_file, stock_price_file, share_capitalization_file,
                 share_income_file, balance_sheet_file, index_price_file):
        self.industry_file = industry_file
        self.stock_price_file = stock_price_file
        self.share_capital_file = share_capitalization_file
        self.share_income_file = share_income_file
        self.balance_sheet_file = balance_sheet_file
        self.index_price_file = index_price_file

        self.stock_price_data = None
        self.industry_data = None
        self.stock_price_calendar_tag = []
        self.share_capital_data = {}
        self.share_capital_change_day = {}
        self.share_income_data = {}
        self.share_income_day = {}
        self.share_income_report_day = {}
        self.industry_contain_company = {}
        self.company_belong_industry = {}
        self.asset_data = {}
        self.debt_data = {}
        self.equity_data = {}
        self.balance_day = {}
        self.balance_report_day = {}
        self.index_price_date = {}
        self.index_price_data = {}

    def wash_stock_price_data(self):  # divide historical data by date
        data = pd.read_csv(self.stock_price_file)
        self.stock_price_data = data.to_numpy()
        guard = 1
        data_size = self.stock_price_data.shape[0]

        start = 0
        end = 1

        while self.stock_price_data[end][guard] == self.stock_price_data[start][guard]:
            end += 1
        self.stock_price_calendar_tag.append(end)
        start = end
        end += 1

        while end < data_size:
            while self.stock_price_data[end][guard] == self.stock_price_data[start][guard]:
                end += 1
                if end == data_size:
                    break
            self.stock_price_calendar_tag.append(end)
            # print(self.stock_price_data[end][guard])
            start = end
            end += 1
        # print(self.stock_price_data)

    def wash_share_capitalization_data(self):  # divide historical data by date
        original_data = pd.read_csv(self.share_capital_file)
        data_array = original_data.to_numpy()
        data_size = len(data_array)

        start = 0
        end = 1

        while end < data_size:
            cur_capital_data = []
            cur_capital_change_day = []
            cur_capital_data.append(data_array[start][1])
            cur_capital_change_day.append(data_array[start][2])
            while data_array[end][0] == data_array[start][0]:
                cur_capital_data.append(data_array[end][1])
                cur_capital_change_day.append(data_array[end][2])
                end += 1
                if end == data_size:
                    break
            self.share_capital_data[data_array[start][0]] = cur_capital_data
            self.share_capital_change_day[data_array[start][0]] = cur_capital_change_day
            start = end
            end += 1

    def wash_share_income_data(self):
        original_data = pd.read_csv(self.share_income_file)
        data_array = original_data.to_numpy()
        sorted_data_array = data_array[data_array[:, 1].argsort()]
        # print(sorted_data_array)
        original_income_data = {}

        for line in sorted_data_array:
            if line[0] not in original_income_data:
                original_income_data[line[0]] = []
                self.share_income_day[line[0]] = []
                self.share_income_report_day[line[0]] = []
            if line[2] == 408001000:
                if np.isnan(line[3]):
                    original_income_data[line[0]].append(0)
                else:
                    original_income_data[line[0]].append(line[3])
                self.share_income_day[line[0]].append(line[1])
                self.share_income_report_day[line[0]].append(line[4])

        for item in original_income_data:

            tem_income_data = []
            if self.share_income_day[item][0] % 10000 == 1231:
                tem_income_data.append(original_income_data[item][0] / 4)
            elif self.share_income_day[item][0] % 10000 == 930:
                tem_income_data.append(original_income_data[item][0] / 3)
            elif self.share_income_day[item][0] % 10000 == 630:
                tem_income_data.append(original_income_data[item][0] / 2)
            else:
                tem_income_data.append(original_income_data[item][0])

            if len(original_income_data[item]) >=2:
                for i in range(1, len(original_income_data[item])):
                    if self.share_income_day[item][i] % 10000 != 331:
                        tem_income_data.append(original_income_data[item][i] - original_income_data[item][i - 1])
                    else:
                        tem_income_data.append(original_income_data[item][i])

            # print(tem_income_data)
            # print(self.share_income_data[item])
            # print(self.share_income_day[item])
            # print(self.share_income_report_day[item])

            income_ytm = []
            income_ytm.append(tem_income_data[0] * 4)
            if len(tem_income_data) >= 2:
                income_ytm.append((tem_income_data[0] + tem_income_data[1]) * 2)
            if len(tem_income_data) >= 3:
                income_ytm.append((tem_income_data[0] + tem_income_data[1] + tem_income_data[2]) * 4 / 3)
            if len(tem_income_data) >= 4:
                for i in range(3, len(tem_income_data)):
                    income_ytm.append(tem_income_data[i - 3] + tem_income_data[i - 2] + tem_income_data[i - 1]
                                      + tem_income_data[i])

            self.share_income_data[item] = income_ytm

        # print(original_income_data['600000.SH'])
        # print(self.share_income_data['600000.SH'])
        # print(self.share_income_day['600000.SH'])
        # print(self.share_income_report_day['600000.SH'])

    def wash_share_income_data_new(self):
        original_data = pd.read_csv(self.share_income_file)
        data_array = original_data.to_numpy()
        sorted_data_array = data_array[data_array[:, 4].argsort()]
        original_income_data = {}

        for line in sorted_data_array:
            if line[1] not in original_income_data:
                original_income_data[line[1]] = []
                self.share_income_day[line[1]] = []
                self.share_income_report_day[line[1]] = []
            if line[5] == 408001000 and (not np.isnan(line[4])):
                if np.isnan(line[63]):
                    original_income_data[line[1]].append(0)
                else:
                    original_income_data[line[1]].append(line[63])
                self.share_income_day[line[1]].append(line[4])
                if np.isnan(line[68]):
                    self.share_income_report_day[line[1]].append(line[4])
                else:
                    self.share_income_report_day[line[1]].append(line[68])

        for item in original_income_data:
            tem_income_data = []
            if self.share_income_day[item][0] % 10000 == 1231:
                tem_income_data.append(original_income_data[item][0] / 4)
            elif self.share_income_day[item][0] % 10000 == 930:
                tem_income_data.append(original_income_data[item][0] / 3)
            elif self.share_income_day[item][0] % 10000 == 630:
                tem_income_data.append(original_income_data[item][0] / 2)
            else:
                tem_income_data.append(original_income_data[item][0])

            if len(original_income_data[item]) >= 2:
                for i in range(1, len(original_income_data[item])):
                    if self.share_income_day[item][i] % 10000 != 331:
                        tem_income_data.append(original_income_data[item][i] - original_income_data[item][i - 1])
                    else:
                        tem_income_data.append(original_income_data[item][i])

            income_ytm = []
            income_ytm.append(tem_income_data[0] * 4)
            if len(tem_income_data) >= 2:
                income_ytm.append((tem_income_data[0] + tem_income_data[1]) * 2)
            if len(tem_income_data) >= 3:
                income_ytm.append((tem_income_data[0] + tem_income_data[1] + tem_income_data[2]) * 4 / 3)
            if len(tem_income_data) >= 4:
                for i in range(3, len(tem_income_data)):
                    income_ytm.append(tem_income_data[i - 3] + tem_income_data[i - 2] + tem_income_data[i - 1]
                                      + tem_income_data[i])

            self.share_income_data[item] = income_ytm

    def wash_balance_data(self):
        original_data = pd.read_csv(self.balance_sheet_file)
        data_array = original_data.to_numpy()
        sorted_data_array = data_array[data_array[:, 4].argsort()]

        for line in sorted_data_array:
            if line[1] not in self.asset_data:
                self.asset_data[line[1]] = []
                self.debt_data[line[1]] = []
                self.equity_data[line[1]] = []
                self.balance_day[line[1]] = []
                self.balance_report_day[line[1]] = []
            if line[5] == 408001000 and (not np.isnan(line[4])):
                self.asset_data[line[1]].append(line[66])
                self.debt_data[line[1]].append(line[117])
                self.equity_data[line[1]].append(line[129])
                self.balance_day[line[1]].append(line[4])
                self.balance_report_day[line[1]].append(line[132])

        # print(self.asset_data['600000.SH'])
        # print(self.debt_data['600000.SH'])
        # print(self.equity_data['600000.SH'])
        # print(self.balance_day['600000.SH'])
        # print(self.balance_report_day['600000.SH'])

    def wash_industry_data(self):
        data = pd.read_csv(self.industry_file)
        self.industry_data = data.to_numpy()
        # self.get_current_industry_data(20180101)

    def get_current_industry_data(self, cur_date):
        self.industry_contain_company = {}
        self.company_belong_industry = {}
        for line in self.industry_data:
            if line[2] <= cur_date:
                if (line[4] == 1) or (line[4] == 0 and line[3] > cur_date):
                    if line[0] not in self.industry_contain_company:
                        self.industry_contain_company[line[0]] = []
                    self.industry_contain_company[line[0]].append(line[1])
                    if line[1] not in self.company_belong_industry:
                        self.company_belong_industry[line[1]] = []
                    self.company_belong_industry[line[1]].append(line[0])
        # print(self.company_belong_industry)
        # print(self.industry_contain_company)
        for item in self.company_belong_industry:
            if len(self.company_belong_industry[item]) > 1:
                print(item, self.company_belong_industry[item])

    def wash_index_price_data(self):  # divide historical data by date
        data = pd.read_csv(self.index_price_file)
        index_price = data.to_numpy()
        for line in index_price:
            if line[0] not in self.index_price_data:
                self.index_price_data[line[0]] = []
                self.index_price_date[line[0]] = []
            self.index_price_data[line[0]].append(line[6])
            self.index_price_date[line[0]].append(line[1])
        # print(self.index_price_date)
        # print(self.index_price_data)

    def execute_wash_data(self):
        self.wash_stock_price_data()
        self.wash_share_capitalization_data()
        self.wash_share_income_data_new()
        self.wash_industry_data()
        self.wash_balance_data()
        self.wash_index_price_data()
