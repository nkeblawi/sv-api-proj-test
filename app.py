import os
import base64
import http.client
from io import BytesIO, StringIO
from flask import Flask, render_template, request
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


### ---------------------------------------------------- ###
### ENVIRONMENT SETUP
### ---------------------------------------------------- ###


# Load environment variables
load_dotenv()
sv_api_key = os.getenv("SV_API_KEY")
sv_url = os.getenv("SV_URL")
sv_api_version = os.getenv("SV_API_VERSION")

# Open a connection to the SV API
conn = http.client.HTTPSConnection(sv_url)
headers = {"Accept": "text/csv, text/html"}

# Set non-interactive backend for matplotlib
matplotlib.use("Agg")

# Start the Flask app in a web browser
app = Flask(__name__)
app.static_folder = "static"


### ---------------------------------------------------- ###
### DATA AND VISUALIZATION FUNCTIONS
### ---------------------------------------------------- ###


# Function to pull data into a dataframe
def pull_data(models, tindex, model_run, date, file_suffix):
    # Initialize a dictionary to hold data for each model
    model_data = {}

    for model in models:
        # Build the connection request URL with all the inputs, API key, and headers
        teleconn_URL = f"/{sv_api_version}/model-data/{model}/{date}/{model_run}/teleconnection/{tindex}{file_suffix}?apikey={sv_api_key}"
        conn.request("GET", teleconn_URL, headers=headers)

        # Get the response
        res = conn.getresponse()
        data = res.read()

        # Decode the byte data into a string and split into lines
        data_str = data.decode("utf-8")
        df = pd.read_csv(StringIO(data_str), header=None)

        # Get the x and y values; average the y values by hour if the model has ensembles
        x_values = df.iloc[0, 1:].astype(int).values
        y = df.iloc[1:, 1:].astype(float).values
        y_values = y.mean(axis=0)

        # Store the data in the model dictionary
        model_data[model] = (x_values, y_values)

    return model_data


# Function to plot the data:
def plot_data(model_data, tindex, model_run, date):
    fig = plt.figure(figsize=(12, 8))  # Set figure size
    ax = fig.add_subplot(111)

    # Plot the data for each model
    for model, (x, y) in model_data.items():
        ax.plot(x, y, marker="o", label=model)

    ax.set_title(tindex.upper() + " Forecast Plot: " + model_run + " " + " " + date)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Daily " + tindex.upper())
    ax.set_ylim(-4, 4)
    ax.axhline(y=0, color="green", linewidth=2, linestyle="--")
    ax.grid(True)
    ax.legend()

    # Save the plot to a BytesIO object and pass it to the /plot/ page
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode("utf8")

    return plot_url


### ---------------------------------------------------- ###
### WEB INTERFACE API ROUTES
### ---------------------------------------------------- ###


# Load the index page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Invoke the API with user inputs and plot the results
@app.route("/plot", methods=["POST"])  # form action "/plot" method="get" in index.html
def submit_request():
    # Get user inputs
    models = request.form.getlist("model")  # Get a list of selected models
    selected_date = request.form["date"]
    date = selected_date.replace("-", "")
    model_run = request.form["model_run"]
    tindex = request.form["tindex"]
    file_suffix = "-forecast.csv"  # hardcoded

    # Pull model data
    model_data = pull_data(models, tindex, model_run, date, file_suffix)

    # Plot the data
    plot_url = plot_data(model_data, tindex, model_run, date)

    # Display the plotted data
    return render_template("index.html", plot_url=plot_url, selected_date=selected_date)


if __name__ == "__main__":
    # Debug mode in development environment
    app.run(debug=False)

    # Production environment
    # server = WSGIServer(('', 8080), app)
    # server.serve_forever()
