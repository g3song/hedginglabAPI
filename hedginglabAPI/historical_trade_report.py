import argparse
import requests

def get_trade(api_key, combo_name, entry_type, start_date_str, end_date_str):
	request_url = "https://www.hedginglab.com" + "/api/beta/v1/earning_batch_trade/?apikey=" + api_key + "&entry_type=" + entry_type + "&start_date_str=" + start_date_str + "&end_date_str=" + end_date_str + "&combo_name=" + combo_name
	response = requests.get(request_url)
	trade_list = response.json()
	return trade_list

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

		trade_profit = round((trade['after_earning_cost'] - trade['entry_cost']) / trade['entry_cost'] * 100, 2)
		if exit_type == "-1":
			trade_profit = round((trade['before_earning_cost'] - trade['entry_cost']) / trade['entry_cost'] * 100, 2)
		if exit_type == "2":
			trade_profit = round((trade['at_expire_1_cost'] - trade['entry_cost']) / trade['entry_cost'] * 100, 2)
		symbol_obj['profit_percentage'] = round(symbol_obj['profit_percentage'] + trade_profit, 2)
		symbol_obj['total_trade'] = symbol_obj['total_trade'] + 1
		if trade_profit >= 0.0:
			symbol_obj['total_winner'] = symbol_obj['total_winner'] + 1
		symbol_obj['winning_perc'] = round(symbol_obj['total_winner'] / symbol_obj['total_trade'] * 100, 2)
		symbol_profit[symbol] = symbol_obj
	return symbol_profit


def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('-k', '--apikey', action='store', dest='api_key', help='API Key', )
	parser.add_argument('-c', '--combo', action='store', dest='combo_name', help='Combo Name', )
	parser.add_argument('-t', '--entrytype', action='store', dest='entry_plan', help='Entry Plan', )
	parser.add_argument('-x', '--exittype', action='store', dest='exit_plan', help='Exit Plan', )
	parser.add_argument('-s', '--sorttype', action='store', dest='sort_type', help='Sort Type', )
	parser.add_argument('-y', '--year', action='store', dest='year_list', help='Year List', )

	args = parser.parse_args()

	combo_name = args.combo_name
	entry_plan = args.entry_plan
	exit_plan = args.exit_plan
	sort_type = args.sort_type
	api_key = args.api_key or "demo"

	# entry type can be -10: 10 days before earnings, -5: 5 days before earnings, -3: 3 days before earnings, -1: 1 day before earning
	if entry_plan == None:
		print ("Default Entry: Before Earnings")
		entry_plan = "-1"

	# exit type can be -1: before earnings, 1: after earnings, 2: at expire date
	if exit_plan == None:
		print ("Default Exit: After Earnings")
		exit_plan = "1"

	# combo name can be one of Call/Put/Straddle/Strangle/IronButterfly/IronCondor/DoubleCalendar/DoubleDiagonal

	symbol_profit = {}
	for year in args.year_list.split(","):
		start_date_str = year + "-01-01"
		end_date_str = year + "-12-31"
		trade_list = get_trade(api_key, combo_name, entry_plan, start_date_str, end_date_str)
		symbol_profit = process_trade_result(trade_list, exit_plan, symbol_profit)

	final_list = []
	for symbol in symbol_profit.keys():
		if symbol_profit[symbol]['total_trade'] > 3:
			final_list.append(symbol_profit[symbol])

	if sort_type == "profit_perc":
		final_list = sorted(final_list, key=lambda i: i['profit_percentage'], reverse=True)
	else:
		final_list = sorted(final_list, key=lambda i: i['winning_perc'], reverse=True)

	for symbol in final_list[:50]:
		print (symbol)



main()
