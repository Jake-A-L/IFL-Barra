import pandas as pd
import numpy as np
import operator
import numpy as np
import matplotlib.pyplot as plt


def get_cur_day_data(trade_day, data_matrix, data_calendar_tag):
    if trade_day == 1:
        cur_day_data = data_matrix[0:data_calendar_tag[trade_day - 1]]
    else:
        cur_day_data = data_matrix[data_calendar_tag[trade_day - 2]: data_calendar_tag[trade_day - 1]]
    return cur_day_data


def get_cur_price_data(cur_day_data):
    cur_average_price = {}
    for line in cur_day_data:
        if line[-1] == '交易' and line[4] != line[5]:
            # cur_average_price[line[0]] = line[10] * line[11]
            cur_average_price[line[0]] = line[17] * line[16]  # new data
    return cur_average_price


def get_close_data(cur_day_data):
    cur_close_price = {}
    for line in cur_day_data:
        # if line[-1] == '交易' and line[4] != line[5]:
            # cur_average_price[line[0]] = line[10] * line[11]
        cur_close_price[line[0]] = line[15]  # new data, 不区分是否交易
    return cur_close_price


def get_start_data(cur_day_data):
    cur_start_price = {}
    for line in cur_day_data:
        if line[-1] == '交易' and line[4] != line[5]:
            # cur_average_price[line[0]] = line[10] * line[11]
            cur_start_price[line[0]] = line[12]  # new data
    return cur_start_price


def calculate_yield_data(trade_day, data_matrix, data_calendar_tag):
    begin_trade_day = trade_day + 1
    begin_trade_data = get_cur_day_data(begin_trade_day, data_matrix, data_calendar_tag)
    begin_trade_price = get_cur_price_data(begin_trade_data)
    end_trade_day = trade_day + 2
    end_trade_data = get_cur_day_data(end_trade_day, data_matrix, data_calendar_tag)
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


def draw_answer(data_matrix, factor_label, index_data):
    # print(data_matrix)
    # print(factor_label)
    # print(data_matrix.shape)
    # print(data_matrix.shape[1])

    fig, ax = plt.subplots()
    x_num = data_matrix.shape[1]
    x = np.linspace(0, x_num, x_num)
    for i in range(len(factor_label)):
        ax.plot(x, data_matrix[i, :], label=factor_label[i])

    for item in index_data:
        ax.plot(x, index_data[item], label=item)
    ax.legend()
    plt.xlabel('trade day number')
    plt.ylabel('total return')
    # plt.show()
    plt.savefig('net value.jpg')