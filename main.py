import streamlit as st
from datetime import date, timedelta

def generate_date_list(start_date, end_date):
  date_list = []
  current_date = start_date
  while current_date <= end_date:
    date_list.append(current_date.strftime("%Y-%m-%d"))
    current_date += timedelta(days=1)
  return date_list

start_date = date(2024, 8, 1)
end_date = date(2024, 12, 31)

date_list = generate_date_list(start_date, end_date)

# Format the list as HTML with strikethrough for past dates
html_list = "<ul>"
for date_str in date_list:
  if date.fromisoformat(date_str) < date.today():
    html_list += f"<li><s>{date_str}</s></li>"
  else:
    html_list += f"<li>{date_str}</li>"
html_list += "</ul>"

st.markdown(html_list, unsafe_allow_html=True)
