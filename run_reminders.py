import streamlit as st
from core.reminder_scheduler import start_scheduler

SENDER_EMAIL = st.secrets["EMAIL_USER"]
SENDER_PASSWORD = st.secrets["EMAIL_PASS"]
USER_EMAIL = st.secrets["USER_EMAIL"]

start_scheduler(SENDER_EMAIL, SENDER_PASSWORD, USER_EMAIL)
