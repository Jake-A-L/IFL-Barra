import numpy as np
import IndustryResolver
import CommonFunction
import matplotlib.pyplot as plt


class FactorEvaluator(object):

    def __init__(self, original_data_washer, market_value_factor, daily_rise_factor, period_rise_factor,
                 amount_rise_factor, financial_factor, high_to_low_factor):
        self.portfolio_value = []
        self.last_stock_value = {}
        self.last_stock_volume = {}
        self.trade_day = 0
        self.history_traded_stock = []
        self.original_data_washer = original_data_washer
        self.market_value_factor = market_value_factor
        self.daily_rise_factor = daily_rise_factor
        self.period_rise_factor = period_rise_factor
        self.amount_rise_factor = amount_rise_factor
        self.financial_factor = financial_factor
        self.high_to_low_factor = high_to_low_factor
        self.factor_ic = {}

    def calculate_factor_ic(self, trade_day):
        invest_yield_data = CommonFunction.calculate_yield_data(trade_day, self.original_data_washer.stock_price_data,
                                                                self.original_data_washer.stock_price_calendar_tag)

        cur_day_data = CommonFunction.get_cur_day_data(trade_day, self.original_data_washer.stock_price_data,
                                                       self.original_data_washer.stock_price_calendar_tag)
        cur_trade_date = cur_day_data[0][1]
        self.original_data_washer.get_current_industry_data(cur_trade_date)

        self.market_value_factor.calculate_market_value_factor(trade_day + 1)

        self.factor_ic['market value'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.market_value_factor.cur_original_market_value_factor,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.factor_ic['non linear market value'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.market_value_factor.non_linear_market_value,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.daily_rise_factor.calculate_second_last_close_price(trade_day)
        self.daily_rise_factor.calculate_daily_rise_factor(trade_day + 1)
        self.factor_ic['momentum'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.daily_rise_factor.cur_original_daily_rise_factor,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.amount_rise_factor.calculate_second_last_amount(trade_day - 1)
        self.amount_rise_factor.calculate_daily_rise_factor(trade_day)
        self.factor_ic['daily amount rise'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.amount_rise_factor.cur_original_amount_rise_factor,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.financial_factor.calculate_ep(trade_day)
        self.factor_ic['ep'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.financial_factor.last_ep,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.high_to_low_factor.calculate_high_to_low_factor(trade_day)
        self.factor_ic['ln high to low'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.high_to_low_factor.cur_high_to_low_factor,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.period_rise_factor.calculate_second_last_close_price(trade_day - 2)
        self.period_rise_factor.calculate_period_rise_factor(trade_day+1)
        self.factor_ic['three day price rise'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.period_rise_factor.cur_original_period_rise_factor,
                self.original_data_washer.industry_contain_company), invest_yield_data))

        self.factor_ic['bp'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.financial_factor.bp_factor, self.original_data_washer.industry_contain_company),
                invest_yield_data))
        self.factor_ic['roe'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.financial_factor.roe_factor, self.original_data_washer.industry_contain_company),
                invest_yield_data))
        self.factor_ic['leverage'].append(
            IndustryResolver.calculate_ic(IndustryResolver.resolve_industry_factor(
                self.financial_factor.leverage_factor, self.original_data_washer.industry_contain_company),
                invest_yield_data))

    def draw_answer(self, data_matrix, length):
        # print(data_matrix)
        # print(factor_label)
        # print(data_matrix.shape)
        # print(data_matrix.shape[1])
        for item in data_matrix:
            fig, ax = plt.subplots()
            x = np.linspace(0, length, length)
            ax.plot(x, data_matrix[item], label=item)
            ax.legend()
            plt.xlabel('trade day number')
            plt.ylabel('IC')
            # plt.show()
            plt.savefig('./factor_ic/' + item + ' factor return ic(cumulative).jpg')

    def back_test(self):
        factor_label = ['market value', 'non linear market value', 'momentum', 'daily amount rise', 'ep',
                        'ln high to low', 'three day price rise', 'bp', 'roe', 'leverage']
        for item in factor_label:
            self.factor_ic[item] = []

        trade_day = 3

        while trade_day < 10:#len(self.original_data_washer.stock_price_calendar_tag) - 2:
            print(trade_day)
            self.calculate_factor_ic(trade_day)
            trade_day += 1

        for item in self.factor_ic:
            for i in range(len(self.factor_ic[item]) - 1):
                self.factor_ic[item][i+1] += self.factor_ic[item][i]

        self.draw_answer(self.factor_ic, len(self.factor_ic['market value']))
