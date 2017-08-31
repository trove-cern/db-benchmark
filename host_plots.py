import os

from flask import Flask, url_for

app = Flask(__name__, static_folder="output_plots")

@app.route("/")
def hello():
    plots = [plot for plot in os.listdir("output_plots") if not plot == "pinned"]
    latest_plot = sorted(plots, key=lambda x: int(x.split(".")[0]))[-1]
    print(latest_plot)
    pinned_plots = sorted(os.listdir("output_plots/pinned/"), key=lambda x: int(x.split(".")[0]))
    pinned_html = "\n".join(["<p>{}</p><img src='{}'/>".format(name, url_for("static", filename=name)) for name in pinned_plots])
    return "<h2>Latest plot:</h2><img src='{}'/><h2>Pinned:</h2>{}".format(url_for("static", filename=latest_plot), pinned_html)

if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=80)
