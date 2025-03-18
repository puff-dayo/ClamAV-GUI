import locale
from datetime import datetime
from ttkbootstrap import ttk

# Force English locale
# locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# Your date parsing code
date_string = 'Sun Mar 16 16:35:38 2025'
date_format = '%a %b %d %H:%M:%S %Y'

try:
    parsed_date = datetime.strptime(date_string, date_format)
    print("Parsed date:", parsed_date)
except ValueError as e:
    print("Error:", e)