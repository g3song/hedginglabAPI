import argparse
import requests

def get_trade(api_key, combo_name, entry_type, start_date_str, end_date_str):
	request_url = "https://www.hedginglab.com" + "/api/beta/v1/earning_batch_trade/?apikey=" + api_key + "&entry_type=" + entry_type + "&start_date_str=" + start_date_str + "&end_date_str=" + end_date_str + "&combo_name=" + combo_name
	response = requests.get(request_url)
	trade_list = response.json()
	return trade_list

def calculate_profit(trade, exit_type):

	trade_profit = 0.0
	if trade['entry_cost'] > 0.0:
		trade_profit = round((trade['after_earning_cost'] - trade['entry_cost']) / trade['entry_cost'] * 100, 2)
		if exit_type == "-1":
			trade_profit = round((trade['before_earning_cost'] - trade['entry_cost']) / trade['entry_cost'] * 100, 2)
		if exit_type == "2":
			trade_profit = round((trade['at_expire_1_cost'] - trade['entry_cost']) / trade['entry_cost'] * 100, 2)
	else:
		# if this is credit trade, use max loss
		if trade['combo_name'] == 'IronCondor':
			trade_result = trade['after_earning_cost'] - trade['entry_cost']
			if exit_type == "-1":
				trade_result = trade['before_earning_cost'] - trade['entry_cost']
			if exit_type == "2":
				trade_result = trade['at_expire_1_cost'] - trade['entry_cost']
			trade_put_cost = abs(trade['strike_1'] - trade['strike_2']) * 100
			trade_call_cost = abs(trade['strike_3'] - trade['strike_4']) * 100
			trade_cost = max(trade_put_cost, trade_call_cost)
			trade_profit = round(trade_result / trade_cost * 100, 2)

	return trade_profit

def process_trade_result(trade_list, exit_type, symbol_profit):
	for trade in trade_list:
		if int(trade['entry_cost']) == 0:
			continue
		if int(trade['strike_1']) < 30:
			continue
		symbol = trade['symbol']
		if symbol in symbol_profit.keys():
			symbol_obj = symbol_profit[symbol]
		else:
			symbol_obj = {}
			symbol_obj['symbol'] = symbol
			symbol_obj['profit_percentage'] = 0.0
			symbol_obj['total_trade'] = 0
			symbol_obj['total_winner'] = 0

		trade_profit = calculate_profit(trade, exit_type)

		symbol_obj['profit_percentage'] = round(symbol_obj['profit_percentage'] + trade_profit, 2)
		symbol_obj['total_trade'] = symbol_obj['total_trade'] + 1
		if trade_profit >= 0.0:
			symbol_obj['total_winner'] = symbol_obj['total_winner'] + 1
		symbol_obj['winning_perc'] = round(symbol_obj['total_winner'] / symbol_obj['total_trade'] * 100, 2)
		symbol_profit[symbol] = symbol_obj
	return symbol_profit


def summarize_trade(combo_name, entry_plan, exit_plan, year_list, api_key):

	symbol_profit = {}
	for year in year_list.split(","):
		start_date_str = year + "-01-01"
		end_date_str = year + "-12-31"
		trade_list = get_trade(api_key, combo_name, entry_plan, start_date_str, end_date_str)
		symbol_profit = process_trade_result(trade_list, exit_plan, symbol_profit)

	return symbol_profit




