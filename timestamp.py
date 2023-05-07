import datetime

# now = datetime.datetime.now()
# current_hour = now.hour

# # Convert the current hour to a Unix timestamp
# current_timestamp = int(datetime.datetime.timestamp(datetime.datetime(now.year, now.month, now.day, current_hour, 0, 0)))

# print(current_timestamp)


timestamp = 1651967066 # Replace this with your Unix timestamp

# Convert Unix timestamp to a datetime object
dt_object = datetime.datetime.fromtimestamp(timestamp)

# Extract hours and minutes from datetime object
hours = dt_object.hour
minutes = dt_object.minute

# Print hours and minutes
print("Hours:", hours)
print("Minutes:", minutes)