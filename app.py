import streamlit as st
import pandas as pd
import http.client
from datetime import datetime
from test_app import pull_data
import matplotlib.pyplot as plt

# Load API key and secrets
sv_api_key = st.secrets.SV_API_KEY
sv_url = st.secrets.SV_URL
sv_api_version = st.secrets.SV_API_VERSION

# Open a connection to the SV API
conn = http.client.HTTPSConnection(sv_url)
headers = {"Accept": "text/csv, text/html"}

# Title and description
st.title("Teleconnection Forecast Plotter")
st.write(
    "Plot the daily teleconnection forecast for each model. Ensemble means will be plotted if ensemble models are selected:"
)

# Pick a model:
models = []
model_inputs = st.multiselect(
    "Pick a model (you can choose more than one):", ["GFS", "GEFS", "ECMWF", "EPS"]
)
for option in model_inputs:
    if option == "GFS":
        models.append("gfs")
    elif option == "GEFS":
        models.append("gfs-ens-mem")
    elif option == "ECMWF":
        models.append("ecmwf")
    elif option == "EPS":
        models.append("ecmwf-eps")

# Pick a model run:
run = st.selectbox("Pick a model run:", ["00z", "06z", "12z", "18z"])

# Select an index
tindex = st.selectbox("Choose a teleconnection index:", ["PNA", "NAO", "EPO"]).lower()

# Date input
selected_date = st.date_input("Select the date:", value=None, format="YYYY-MM-DD")

# Plot the graph
if st.button("Plot"):
    file_suffix = "-forecast.csv"  # hardcoded
    date = str(selected_date).replace("-", "")

    # Pull model data
    model_data = pull_data(models, tindex, run, date, file_suffix)

    # Plot the data
    fig = plt.figure(figsize=(12, 8))  # Set figure size
    ax = fig.add_subplot(111)

    for model, (x, y) in model_data.items():
        ax.plot(x, y, marker="o", label=model)

    ax.set_title(tindex.upper() + " Forecast Plot: " + run + " " + " " + date)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Daily " + tindex.upper())
    ax.set_ylim(-4, 4)
    ax.axhline(y=0, color="green", linewidth=2, linestyle="--")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
