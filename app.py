import os
import base64
import http.client
from io import BytesIO
from flask import Flask, render_template, request
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import matplotlib
import matplotlib.pyplot as plt

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

    # Initialize a dictionary to hold data for each model
    model_data = {}

    # Loop through each selected model and make API requests
    for model in models:
        # Build the connection request URL with all the inputs, API key, and headers
        teleconn_URL = f"/{sv_api_version}/model-data/{model}/{date}/{model_run}/teleconnection/{tindex}{file_suffix}?apikey={sv_api_key}"
        conn.request("GET", teleconn_URL, headers=headers)

        # Get the response
        res = conn.getresponse()
        data = res.read()

        # Decode the byte data into a string and split the x and y values
        data_str = data.decode("utf-8")
        x_str, y_str = data_str.split("\n", 1)
        x_str = x_str.split(",")[1:]  # Remove the 'member' part
        y_str = y_str.strip().split(",")[
            1:
        ]  # Strip the trailing \n and remove the leading 0

        # Convert x to integers and y to floating-point numbers
        x = [int(i) for i in x_str]
        y = [float(i) for i in y_str]

        # Store the data in the model dictionary
        model_data[model] = (x, y)

    # Plot the data
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

    return render_template("index.html", plot_url=plot_url, selected_date=selected_date)


if __name__ == "__main__":
    # Debug mode in development environment
    app.run(debug=False)

    # Production environment
    # server = WSGIServer(('', 8080), app)
    # server.serve_forever()
