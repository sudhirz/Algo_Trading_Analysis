from datetime import datetime


start_time = datetime.now()

end_time = datetime.now()

print('start time: {} \n end time: {}' .format(start_time,end_time))

start_date = datetime.datetime.now() - datetime.timedelta(days=365) # one year ago
print(start_date)