# get industry data from initial data
# get factor data
# divide factor data according to industry
# for data in each industry, delete extraordinary data, transform data
# calculate IC and IR
from scipy.stats import mstats
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression, Ridge
import pandas as pd
import numpy as np


def resolve_industry_factor(original_data, industry_contain_company):  # delete industry factor and extraordinary value
    resolved_data = {}
    for industry in industry_contain_company:
        company_factor_value = []
        company_list = []
        for company in industry_contain_company[industry]:
            if company in original_data:
                company_list.append(company)
                company_factor_value.append(original_data[company])
        limits = (1/len(company_factor_value), 1/len(company_factor_value))
        delete_extra_answer = mstats.winsorize(company_factor_value, limits)
        # print(len(delete_extra_answer.data))
        standard_answer = preprocessing.scale(delete_extra_answer.data)
        # print(standard_answer)
        resolved_data.update(dict(zip(company_list, standard_answer)))
    return resolved_data


def calculate_ic(factor_data, invest_yield_data):
    factor_value = []
    invest_yield_value = []
    for company in factor_data:
        if company in invest_yield_data:
            factor_value.append(factor_data[company])
            invest_yield_value.append(invest_yield_data[company])

    df = pd.DataFrame({'factor_value': factor_value, 'invest_yield_value': invest_yield_value})
    ic = df.corr('pearson')
    return ic.values[0][1]


def calculate_ir(factor_data):
    daily_ir = np.mean(factor_data) / np.std(factor_data)
    return daily_ir


def delete_different_data(x1, x2, x3, x4, x5, x6, x7, x8, x9):
    first_factor = []
    second_factor = []
    third_factor = []
    forth_factor = []
    fifth_factor = []
    sixth_factor = []
    seventh_factor = []
    eighth_factor = []
    ninth_factor = []
    target_company = []
    for company in x1:
        if (company in x2) and (company in x3) and (company in x4) and (company in x5) and(company in x6) \
                and (company in x7) and (company in x8) and (company in x9):
            target_company.append(company)
            first_factor.append(x1[company])
            second_factor.append(x2[company])
            third_factor.append(x3[company])
            forth_factor.append(x4[company])
            fifth_factor.append(x5[company])
            sixth_factor.append(x6[company])
            seventh_factor.append(x7[company])
            eighth_factor.append((x8[company]))
            ninth_factor.append(x9[company])
    length = len(first_factor)
    return target_company, np.array(first_factor).reshape(length,1), np.array(second_factor).reshape(length,1),\
           np.array(third_factor).reshape(length,1), np.array(forth_factor).reshape(length,1), \
           np.array(fifth_factor).reshape(length,1), np.array(sixth_factor).reshape(length,1), \
           np.array(seventh_factor).reshape(length,1), np.array(eighth_factor).reshape(length,1), \
           np.array(ninth_factor).reshape(length,1)


def delete_different_data_new(original_factor_data):
    target_company = []
    factor_data = []
    for i in range(len(original_factor_data)):
        factor_data.append([])
    temp_data = original_factor_data[0]
    for company in temp_data:
        guard = 1
        for j in range(len(original_factor_data) - 1):
            if company not in original_factor_data[j+1]:
                guard = 0
                break
        if 1 == guard:
            target_company.append(company)
            for k in range(len(original_factor_data)):
                factor_data[k].append(original_factor_data[k][company])
    return target_company, factor_data


def delete_special_company(factor_matrix, target_company, invest_yield_data):
    resolved_yield_answer = []
    resolved_factor_matrix = []
    for i in range(len(factor_matrix)):
        if target_company[i] in invest_yield_data:
            resolved_yield_answer.append(invest_yield_data[target_company[i]])
            resolved_factor_matrix.append(factor_matrix[i])
    return np.array(resolved_factor_matrix), resolved_yield_answer


def delete_correlation(first_factor, second_factor):
    # lr = LinearRegression()
    lr = Ridge()
    lr.fit(first_factor, second_factor)
    y_predict = lr.predict(first_factor)

    return np.concatenate((first_factor, np.subtract(second_factor, y_predict)), axis=1)


def get_linear_regression_coef(x, y):
    #lr = LinearRegression()
    lr = Ridge()
    lr.fit(x, y)
    # print(lr.coef_)
    return lr.coef_.reshape(x.shape[1], 1)