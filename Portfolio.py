import pandas as pd
import numpy as np
import operator
import numpy as np
import OriginalDataWasher
import MarketValueFactor
import DailyRiseFactor
import AmountRiseFactor
import FinancialFactor
import HighToLowFactor
import IndustryResolver
import PeriodRiseFactor
import CommonFunction
import matplotlib.pyplot as plt


class Portfolio(object):

    def __init__(self, original_data_washer, market_value_factor, daily_rise_factor, period_rise_factor,
                 amount_rise_factor, financial_factor, high_to_low_factor
                 ):
        self.portfolio_value = []
        self.last_stock_value = {}
        self.last_stock_volume = {}
        self.trade_day = 0
        self.history_traded_stock = []
        self.original_data_washer = original_data_washer
        # self.stock_price_data = stock_price_data
        # self.stock_price_calendar_tag = stock_price_calendar_tag

        """
            Plug in factors
        """
        self.market_value_factor = market_value_factor
        self.daily_rise_factor = daily_rise_factor
        self.period_rise_factor = period_rise_factor
        self.amount_rise_factor = amount_rise_factor
        self.financial_factor = financial_factor
        self.high_to_low_factor = high_to_low_factor
        # self.factor_coef = factor_coef
        self.start_value = 100000000

    def calculate_factor(self, trade_day):
        original_factor_data = []
        cur_day_data = CommonFunction.get_cur_day_data(trade_day, self.original_data_washer.stock_price_data,
                                                       self.original_data_washer.stock_price_calendar_tag)
        cur_trade_date = cur_day_data[0][1]
        self.original_data_washer.get_current_industry_data(cur_trade_date)

        self.market_value_factor.calculate_market_value_factor(trade_day + 1)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.market_value_factor.cur_original_market_value_factor,
            self.original_data_washer.industry_contain_company))
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.market_value_factor.non_linear_market_value, self.original_data_washer.industry_contain_company))

        self.daily_rise_factor.calculate_second_last_close_price(trade_day)
        self.daily_rise_factor.calculate_daily_rise_factor(trade_day + 1)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.daily_rise_factor.cur_original_daily_rise_factor, self.original_data_washer.industry_contain_company))

        self.amount_rise_factor.calculate_second_last_amount(trade_day - 1)
        self.amount_rise_factor.calculate_daily_rise_factor(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.amount_rise_factor.cur_original_amount_rise_factor,
            self.original_data_washer.industry_contain_company))

        self.financial_factor.calculate_ep(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.financial_factor.last_ep, self.original_data_washer.industry_contain_company))

        self.high_to_low_factor.calculate_high_to_low_factor(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.high_to_low_factor.cur_high_to_low_factor, self.original_data_washer.industry_contain_company))

        self.period_rise_factor.calculate_second_last_close_price(trade_day - 2)
        self.period_rise_factor.calculate_period_rise_factor(trade_day+1)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.period_rise_factor.cur_original_period_rise_factor,
            self.original_data_washer.industry_contain_company))

        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.financial_factor.bp_factor, self.original_data_washer.industry_contain_company))
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.financial_factor.roe_factor, self.original_data_washer.industry_contain_company))
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            self.financial_factor.leverage_factor, self.original_data_washer.industry_contain_company))

        target_company, resolved_data = IndustryResolver.delete_different_data_new(original_factor_data)
        factor_matrix = np.array(resolved_data[0]).reshape(len(target_company), 1)
        for j in range(len(resolved_data) - 1):
            factor_matrix = \
                IndustryResolver.delete_correlation(factor_matrix,
                                                    np.array(resolved_data[j+1]).reshape(len(target_company), 1))

        factor_matrix = CommonFunction.insert_industry_factor(target_company, factor_matrix,
                                                              self.original_data_washer.industry_contain_company,
                                                              self.original_data_washer.company_belong_industry)
        return target_company, factor_matrix

    def get_factor_coefficient(self, target_company, factor_matrix, trade_day):
        # factor_coef_matrix = None
        invest_yield_data = CommonFunction.calculate_yield_data(trade_day, self.original_data_washer.stock_price_data,
                                                                self.original_data_washer.stock_price_calendar_tag)
        resolved_factor_matrix, resolved_yield_data = IndustryResolver.delete_special_company(
            factor_matrix.tolist(), target_company, invest_yield_data)
        cur_factor_coef = IndustryResolver.get_linear_regression_coef(resolved_factor_matrix, resolved_yield_data)
        # factor_coef_matrix = CommonFunction.resolve_factor_coef_matrix(factor_coef_matrix, cur_factor_coef)
        return cur_factor_coef

    def select_stock(self, cur_factor_coef, factor_matrix, target_company):
        factor_score = np.dot(factor_matrix, cur_factor_coef)
        factor_score_matrix = {}
        for i in range(len(target_company)):
            factor_score_matrix[target_company[i]] = factor_score[i][0]
        sorted_score_matrix = sorted(factor_score_matrix.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_score_matrix

    def trade_stock(self, trade_day, sorted_score_matrix, target_portfolio_num):
        cur_target_stock = []
        cur_day_data = CommonFunction.get_cur_day_data(trade_day, self.original_data_washer.stock_price_data,
                                                       self.original_data_washer.stock_price_calendar_tag)
        cur_start_price = CommonFunction.get_start_data(cur_day_data)
        cur_average_price = CommonFunction.get_cur_price_data(cur_day_data)
        count = 0

        while count < target_portfolio_num:
            if sorted_score_matrix[count][0] in cur_start_price:
                cur_target_stock.append(sorted_score_matrix[count][0])
                count += 1

        if trade_day == 5:
            for item in cur_target_stock:
                self.last_stock_volume[item] = self.start_value/target_portfolio_num/cur_average_price[item] * 0.999
        else:
            last_available_stock = []
            last_not_available_stock = []
            for item in self.last_stock_value:
                if item not in cur_average_price:
                    last_not_available_stock.append(item)
                    if item in cur_target_stock:
                        cur_target_stock.remove(item)
                else:
                    last_available_stock.append(item)
            adjust_value = self.portfolio_value[trade_day - 6]  # 假如不是一天期，这个初始组合值要改成当日开盘值

            cur_stock_volume = {}
            for item in last_not_available_stock:
                adjust_value -= self.last_stock_value[item]
                cur_stock_volume[item] = self.last_stock_volume[item]

            for item in last_available_stock:
                if item not in cur_target_stock:
                    adjust_value -= (self.last_stock_value[item] - self.last_stock_volume[item] *
                                     cur_average_price[item] * 0.998)  # 卖出不再持有的股票

            average_value = adjust_value/len(cur_target_stock)
            for item in cur_target_stock:
                if item in last_available_stock and self.last_stock_value[item] < average_value:
                    cur_stock_volume[item] = (average_value - self.last_stock_value[item]) * 0.999 / \
                                             cur_average_price[item] + self.last_stock_volume[item]
                if item in last_available_stock and self.last_stock_value[item] > average_value:
                    cur_stock_volume[item] = self.last_stock_volume[item] - \
                                             (self.last_stock_value[item] - average_value) * 1.002 / \
                                             cur_average_price[item]
                if item not in last_available_stock:
                    cur_stock_volume[item] = average_value * 0.999 / cur_average_price[item]

            self.last_stock_volume = cur_stock_volume

    def calculate_total_yield(self, trade_day):
        cur_day_data = CommonFunction.get_cur_day_data(trade_day, self.original_data_washer.stock_price_data,
                                                       self.original_data_washer.stock_price_calendar_tag)
        cur_close_price = CommonFunction.get_close_data(cur_day_data)

        total_value = 0
        cur_stock_value = {}

        for item in self.last_stock_volume:
            if item in cur_close_price:
                cur_stock_value[item] = self.last_stock_volume[item] * cur_close_price[item]
            else:
                cur_stock_value[item] = self.last_stock_value[item]
            total_value += cur_stock_value[item]

        self.last_stock_value = cur_stock_value
        self.portfolio_value.append(total_value)

    def get_index_data(self, start_day, length):
        start_day_data = CommonFunction.get_cur_day_data(start_day, self.original_data_washer.stock_price_data,
                                                         self.original_data_washer.stock_price_calendar_tag)
        start_trade_date = start_day_data[0][1]
        period_index_data = {}
        for item in self.original_data_washer.index_price_date:
            count = 0
            while count< len(self.original_data_washer.index_price_date[item]):
                if self.original_data_washer.index_price_date[item][count] == start_trade_date:
                    period_index_data[item] = []
                    for value in self.original_data_washer.index_price_data[item][count:count+length]:
                        period_index_data[item].append(value/self.original_data_washer.index_price_data[item][count])
                    break
                else:
                    count += 1
        return period_index_data

    def back_test(self):
        trade_day = 3

        while trade_day < len(self.original_data_washer.stock_price_calendar_tag) - 2:
            target_company, factor_matrix = self.calculate_factor(trade_day)
            cur_factor_coef = self.get_factor_coefficient(target_company, factor_matrix, trade_day)
            target_company, factor_matrix = self.calculate_factor(trade_day+1)
            sorted_score_matrix = self.select_stock(cur_factor_coef, factor_matrix, target_company)
            self.trade_stock(trade_day+2, sorted_score_matrix, 100)
            self.calculate_total_yield(trade_day+2)
            print('trade day:' + str(trade_day+2))
            # print(self.portfolio_value[trade_day - 4] / 100000000)
            trade_day += 1
        output_value = []
        for item in self.portfolio_value:
            output_value.append(item/self.start_value)
        print(output_value)

        CommonFunction.draw_answer(np.asarray(output_value).reshape(1, len(self.portfolio_value)),
                                   ['first model'],
                                   # self.get_index_data(5, 100-3)
                                   self.get_index_data(5, len(self.original_data_washer.stock_price_calendar_tag) - 5)
                                   )
