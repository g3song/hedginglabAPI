import argparse
import requests

from trade_history_lib import summarize_trade, get_trade, process_trade_result

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

	symbol_profit = summarize_trade(combo_name, entry_plan, exit_plan, "2019,2020", api_key)
	final_list = []
	for symbol in symbol_profit.keys():
		# filter results, minimum trade 10
		#winning_perc = symbol_profit[symbol]['total_winner'] / symbol_profit[symbol]['total_trade']
		if symbol_profit[symbol]['total_trade'] >= 4 and symbol_profit[symbol]['winning_perc'] >= 40 and symbol_profit[symbol]['profit_percentage'] > 0.0:
			final_list.append(symbol_profit[symbol])

	final_list = sorted(final_list, key=lambda i: i['winning_perc'], reverse=True)

	qualified_symbol = []
	for symbol in final_list[:50]:
		#print (symbol)
		qualified_symbol.append(symbol['symbol'])

	print ("Top Performed Stocks: ", qualified_symbol)

	# from the list, find earnings date for Q1 2021, and test each trade
	start_date_str = "2021-01-01"
	end_date_str = "2021-03-31"
	back_test_trade_list = get_trade(api_key, combo_name, entry_plan, start_date_str, end_date_str)

	total_profit = 0.0
	print ("Symbol,Trade Date,Lot Size,Entry Cost,After Earning Cost,At Expiry Cost")
	for trade in back_test_trade_list:
		if trade['symbol'] in qualified_symbol:
			# find the trade
			#print (trade)
			# proportion to 2K Max Cost
			max_loss = abs(trade['strike_1'] - trade['strike_2']) * 100
			lot_size = round(2000 / max_loss, 2)

			#print (trade, lot_size)
			#trade_profit = (trade['after_earning_cost'] - trade['entry_cost']) * lot_size
			trade_profit = (trade['at_expire_1_cost'] - trade['entry_cost']) * lot_size
			total_profit = total_profit + trade_profit
			print ("{0},{1},{2},{3},{4},{5}".format(trade['symbol'], trade['trade_date'], lot_size, trade['entry_cost'], trade['after_earning_cost'], trade['at_expire_1_cost']))

	print ("Net Profit: ", total_profit)





main()
