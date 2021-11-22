from datetime import datetime

date = "2021-11-22"
date_parsed = datetime.strptime(date, '%Y-%m-%d')
print(date_parsed.strftime('%a'))