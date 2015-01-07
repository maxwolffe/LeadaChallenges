"""
Solutions by Max Wolffe to Team Leada Challenge Set 1

Jan 6, 2015
"""
import sys, csv

from heapq import heappush, heappop

"""
Returns a dictionary with keys (1 - size) that all have value zero
"""
def zeroed_dictionary(size):
	return_dict = dict.fromkeys([month for month in range(1,size + 1)])
	for key in range(1, size + 1):
		return_dict[key] = 0 
	return return_dict 

"""
Returns a dictionary of month to average durations of rides started in that month, with a final entry for total average duration. 
"""
def average_durations(monthly_rides, monthly_duration):
	average_durations = {}
	total_time = 0
	total_rides = 0
	for month in range(1,13):
		month_rides = monthly_rides[month]
		month_duration = monthly_duration[month] / 60
		if month_rides > 0:
			total_rides += month_rides
			total_time += month_duration
			average_durations[month] = month_duration / month_rides
	average_durations["Total"] = total_time / total_rides
	return average_durations

"""
Takes a date string and turns it into a float, which can serve as a valid heap key
"""
def numberify_date(date_string):
	number = 0
	month_day_year = date_string.split()[0]
	time = float(date_string.split()[1].replace(":", "."))
	month_day_year = month_day_year.split("/")
	month = int(month_day_year[0])
	day = int(month_day_year[1])
	year = int(month_day_year[2])
	number = year * 1e6 + month * 1e4 + day * 1e2 + time
	return number

def parse_date(date_number):
	time = date_number % 100
	date_number //= 100
	day = date_number % 100
	date_number //= 100
	month = date_number % 100
	date_number //= 100
	year = date_number % 100
	return (int(month), int(day), int(year), time)

"""
Reads the input file one line at a time. 
Collects the date and duration of each ride to compile average durations for each month and total average duration. 
To determine when the first unbalancing occurs, I maintain a heap of bicycles currently in use, where the key is their return time, 
and the total number of bicylces at each terminal in a dictionary. 
For each outgoing bicyle, I check to see if there are any outgoing bicycles that were returned before that bicycle left, and adjust total
terminal counts accordingly. If the outgoing bicycle brings the terminal count of the terminal it is leaving down to zero, then unbalancing has occured. 
"""
def main(argv):
	monthly_duration = zeroed_dictionary(12)
	monthly_rides = zeroed_dictionary(12)
	rides_by_date = {}
	out_bike_heap = []
	terminal_bike_count = {}
	first_unbalanced_terminal = None
	first_unbalanced_time = None
	balanced = True

	if len(argv) == 0:
		print("Insufficient Arguments, please specify an input file")
		return 

	with open(argv[0], 'r') as read_file:
		reader = csv.reader(read_file)
		for line in reader:
			if line[0] == "Trip ID":
				continue
			out_terminal = line[4]
			out_time = numberify_date(line[2])
			return_terminal = line[7]
			return_time = numberify_date(line[5])
			date = line[2].split()[0]
			month = int(line[2].split('/')[0])
			monthly_duration[month] += int(line[1])
			monthly_rides[month] += 1
			if date in rides_by_date:
				rides_by_date[date] += 1
			else:
				rides_by_date[date] = 0

			# Bicycle balancing
			if balanced:
				first_return = (float('inf'), None)
				if len(out_bike_heap) > 0:
					first_return = heappop(out_bike_heap)

				while len(out_bike_heap) >= 0 and out_time > first_return[0]:
					if first_return[1] in terminal_bike_count:
						terminal_bike_count[first_return[1]] += 1
					else:
						terminal_bike_count[first_return[1]] = 31
					first_return = (float('inf'), None)
					if len(out_bike_heap) > 0:
						first_return = heappop(out_bike_heap)

				if out_terminal in terminal_bike_count:
					terminal_bike_count[out_terminal] -= 1
				else:
					terminal_bike_count[out_terminal] = 29

				if terminal_bike_count[out_terminal] == 0:
					balanced = False
					first_unbalanced_terminal = out_terminal
					first_unbalanced_time = parse_date(out_time)

				if first_return[0] != float('inf'):
					heappush(out_bike_heap, first_return)
				heappush(out_bike_heap, (return_time, return_terminal))



		compiled_averages = average_durations(monthly_rides, monthly_duration)
		most_popular_date = max(rides_by_date.keys(), key=(lambda key: rides_by_date[key]))

		if len(argv) == 1:
			print("Month : Average Duration")
			for month in compiled_averages.keys():
				print(str(month) + " : " + str(compiled_averages[month]))
			print("Most Popular Date: " + most_popular_date + " - " + str(rides_by_date[most_popular_date]) + " rides.")
			print("Unbalanced at terminal " + str(first_unbalanced_terminal) + " at date and time (month, day, year, time) " + str(first_unbalanced_time))
		else:
			with open(argv[1], 'w') as write_file:
				write_file.write("Month : Average Duration\n") 
				for month in compiled_averages.keys():
					write_file.write(str(month) + " : " + str(compiled_averages[month]) + " \n")
				write_file.write("Most Popular Date: " + most_popular_date + " - " + str(rides_by_date[most_popular_date]) + " rides.\n")
				write_file.write("Unbalanced at terminal " + str(first_unbalanced_terminal) + " at date and time (month, day, year, time) " + str(first_unbalanced_time) + "\n")




"""
First command line argument specifies input file (bike_trip_data.csv) location. 
Second command line argument (if present) specifies output location.
Additional arguments will be ignored

Expects an input csv with the following columns:
Trip ID,Duration,Start Date,Start Station,Start Terminal,End Date,End Station,End Terminal,Bike #,Subscription Type,Zip Code


"""
if __name__ == "__main__":
   main(sys.argv[1:])



