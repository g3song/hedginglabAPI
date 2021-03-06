import argparse
import requests

from trade_history_lib import summarize_trade

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

	symbol_profit = summarize_trade(combo_name, entry_plan, exit_plan, args.year_list, api_key)

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
