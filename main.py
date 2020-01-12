import pandas as pd
import numpy as np
import OriginalDataWasher
import MarketValueFactor
import DailyRiseFactor
import AmountRiseFactor
import FinancialFactor
import HighToLowFactor
import IndustryResolver
import PeriodRiseFactor
import Portfolio
import FactorEvaluator
import matplotlib.pyplot as plt


def get_cur_day_data(trade_day):
    if trade_day == 1:
        cur_day_data = original_data_washer.stock_price_data[0:original_data_washer.stock_price_calendar_tag[trade_day - 1]]
    else:
        cur_day_data = original_data_washer.stock_price_data[original_data_washer.stock_price_calendar_tag[trade_day - 2]:
                                                             original_data_washer.stock_price_calendar_tag[trade_day - 1]]
    return cur_day_data


def get_cur_price_data(cur_day_data):
    cur_average_price = {}
    for line in cur_day_data:
        if line[-1] == '交易' and line[4] != line[5]:
            # cur_average_price[line[0]] = line[10] * line[11]
            cur_average_price[line[0]] = line[17] * line[16]  # new data
    return cur_average_price


def calculate_yield_data(trade_day):
    begin_trade_day = trade_day + 1
    begin_trade_data = get_cur_day_data(begin_trade_day)
    begin_trade_price = get_cur_price_data(begin_trade_data)
    end_trade_day = trade_day + 2
    end_trade_data = get_cur_day_data(end_trade_day)
    end_trade_price = get_cur_price_data(end_trade_data)
    invest_yield_data = {}
    for stock in begin_trade_price:
        if stock in end_trade_price:
            invest_yield_data[stock] = (end_trade_price[stock] - begin_trade_price[stock]) / begin_trade_price[stock]
    return invest_yield_data


def resolve_factor_coef_matrix(factor_coef_matrix, cur_factor_coef):
    if factor_coef_matrix is None:
        return cur_factor_coef
    else:
        cummulative_factor_coef = np.add(factor_coef_matrix[:, [-1]], cur_factor_coef)
        return np.concatenate((factor_coef_matrix, cummulative_factor_coef), axis=1)


def insert_industry_factor(target_company, factor_matrix, industry_comtain_company, company_belong_industry):
    company_num = len(target_company)
    factor_num = len(industry_comtain_company.keys())
    if factor_num < 29:
        factor_num = 29
    industry_factor = np.zeros((company_num, factor_num))
    for i in range(company_num):
        industry = company_belong_industry[target_company[i]][0]
        column = int(industry[-5:-3])
        industry_factor[i][column-1] = 1
    return np.concatenate((industry_factor, factor_matrix), axis=1)


def draw_answer(data_matrix, industry_label, factor_label):
    print(data_matrix)
    print(industry_label)
    print(factor_label)
    print(data_matrix.shape)
    print(data_matrix.shape[1])

    fig, ax = plt.subplots()
    x_num = data_matrix.shape[1]
    x = np.linspace(0, x_num, x_num)
    for i in range(len(industry_label)):
        ax.plot(x, data_matrix[i, :], label=industry_label[i])
    ax.legend()
    plt.xlabel('trade day number')
    plt.ylabel('factor coefficient')
    plt.savefig('industry_factor.jpg')

    fig, ax = plt.subplots()
    x_num = data_matrix.shape[1]
    x = np.linspace(0, x_num, x_num)
    for i in range(len(factor_label)):
        ax.plot(x, data_matrix[i+29, :], label=factor_label[i])
    ax.legend()
    plt.xlabel('trade day number')
    plt.ylabel('factor coefficient')
    plt.savefig('other_factor.jpg')


def evaluate_factor():
    factor_coef_matrix = None
    trade_day = 4
    while trade_day < len(original_data_washer.stock_price_calendar_tag) - 1:  # len(original_data_washer.stock_price_calendar_tag):
        original_factor_data = []
        cur_day_data = get_cur_day_data(trade_day)
        cur_trade_date = cur_day_data[0][1]
        original_data_washer.get_current_industry_data(cur_trade_date)

        market_value_factor.calculate_market_value_factor(trade_day + 1)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            market_value_factor.cur_original_market_value_factor, original_data_washer.industry_contain_company))
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            market_value_factor.non_linear_market_value, original_data_washer.industry_contain_company))

        daily_rise_factor.calculate_second_last_close_price(trade_day - 1)
        daily_rise_factor.calculate_daily_rise_factor(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            daily_rise_factor.cur_original_daily_rise_factor, original_data_washer.industry_contain_company))

        amount_rise_factor.calculate_second_last_amount(trade_day - 1)
        amount_rise_factor.calculate_daily_rise_factor(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            amount_rise_factor.cur_original_amount_rise_factor, original_data_washer.industry_contain_company))

        financial_factor.calculate_ep(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            financial_factor.last_ep, original_data_washer.industry_contain_company))

        high_to_low_factor.calculate_high_to_low_factor(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            high_to_low_factor.cur_high_to_low_factor, original_data_washer.industry_contain_company))

        period_rise_factor.calculate_second_last_close_price(trade_day - 3)
        period_rise_factor.calculate_period_rise_factor(trade_day)
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            period_rise_factor.cur_original_period_rise_factor, original_data_washer.industry_contain_company))

        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            financial_factor.bp_factor, original_data_washer.industry_contain_company))
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            financial_factor.roe_factor, original_data_washer.industry_contain_company))
        original_factor_data.append(IndustryResolver.resolve_industry_factor(
            financial_factor.leverage_factor, original_data_washer.industry_contain_company))

        target_company, resolved_data = IndustryResolver.delete_different_data_new(original_factor_data)
        factor_matrix = np.array(resolved_data[0]).reshape(len(target_company), 1)
        for j in range(len(resolved_data) - 1):
            factor_matrix = \
                IndustryResolver.delete_correlation(factor_matrix,
                                                    np.array(resolved_data[j+1]).reshape(len(target_company), 1))

        factor_matrix = insert_industry_factor(target_company, factor_matrix,
                                               original_data_washer.industry_contain_company,
                                               original_data_washer.company_belong_industry)
        invest_yield_data = calculate_yield_data(trade_day)
        resolved_factor_matrix, resolved_yield_data = IndustryResolver.delete_special_company(
            factor_matrix.tolist(), target_company, invest_yield_data)
        cur_factor_coef = IndustryResolver.get_linear_regression_coef(resolved_factor_matrix, resolved_yield_data)
        factor_coef_matrix = resolve_factor_coef_matrix(factor_coef_matrix, cur_factor_coef)
        print(trade_day)
        trade_day += 1

    factor_label = ['market value', 'non_linear_market_value', 'momentum', 'daily_amount_rise', 'ep', 'ln_high_to_low',
                    'three_day_price_rise', 'bp', 'roe', 'leverage']  #
    draw_answer(factor_coef_matrix, list(original_data_washer.industry_contain_company.keys()), factor_label)
    pd.DataFrame(factor_coef_matrix).to_csv('factor coefficient.csv')


if __name__ == '__main__':

    original_data_washer = OriginalDataWasher.OriginalDataWasher('./data/指数和行业成分股/AIndexMembersCitics.csv',
                                                                 './data/AShare.csv',
                                                                 './data/A股股本数据/AShareCapitalization.csv',
                                                                 './data/财务数据全/ashareincome.csv',
                                                                 './data/财务数据全/asharebalancesheet.csv',
                                                                 './data/指数日行情/AIndexEODPrices 300_500_800.csv')

    original_data_washer.execute_wash_data()


    """
    Calculate Different Factors
    """
    market_value_factor = MarketValueFactor.MaketValueFactor(original_data_washer.stock_price_data,
                                                             original_data_washer.stock_price_calendar_tag,
                                                             original_data_washer.share_capital_data,
                                                             original_data_washer.share_capital_change_day,
                                                             10, 10)

    daily_rise_factor = DailyRiseFactor.DailyRisefactor(original_data_washer.stock_price_data,
                                                        original_data_washer.stock_price_calendar_tag,
                                                        10, 5)

    period_rise_factor = PeriodRiseFactor.PeriodRisefactor(original_data_washer.stock_price_data,
                                                           original_data_washer.stock_price_calendar_tag,
                                                           10, 5)

    amount_rise_factor = AmountRiseFactor.AmountRiseFactor(original_data_washer.stock_price_data,
                                                           original_data_washer.stock_price_calendar_tag,
                                                           10, 10)

    financial_factor = FinancialFactor.FinancialFactor(original_data_washer.stock_price_data,
                                                       original_data_washer.stock_price_calendar_tag,
                                                       original_data_washer.share_capital_data,
                                                       original_data_washer.share_capital_change_day,
                                                       original_data_washer.share_income_data,
                                                       original_data_washer.share_income_day,
                                                       original_data_washer.share_income_report_day,
                                                       original_data_washer.asset_data,
                                                       original_data_washer.debt_data,
                                                       original_data_washer.equity_data,
                                                       original_data_washer.balance_day,
                                                       10, 10)

    high_to_low_factor = HighToLowFactor.HighToLowFactor(original_data_washer.stock_price_data,
                                                         original_data_washer.stock_price_calendar_tag,
                                                         10, 10)
    # Initiate BackTest
    factor_evaluator = FactorEvaluator.FactorEvaluator(original_data_washer, market_value_factor, daily_rise_factor,
                                                       period_rise_factor, amount_rise_factor, financial_factor,
                                                       high_to_low_factor)
    factor_evaluator.back_test()