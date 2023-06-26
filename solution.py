
# import the necessary libraries 
import datetime 

# get the current date
now = datetime.datetime.now()

# subtract 7 days from the current date
date_one_week_ago = now - datetime.timedelta(days = 7)

# print the date one week ago 
print(date_one_week_ago.strftime("%m/%d/%Y"))