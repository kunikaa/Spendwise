from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CHART_FOLDER = "static/charts"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CHART_FOLDER"] = CHART_FOLDER

# Make sure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    charts = []  # store paths of charts

    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Read CSV
            df = pd.read_csv(filepath)

            # ✅ Pie Chart
            category_summary = df.groupby("Category")["Amount"].sum()
            plt.figure(figsize=(6,6))
            category_summary.plot(kind="pie", autopct="%1.1f%%")
            plt.title("Expense Distribution by Category")
            pie_path = os.path.join(app.config["CHART_FOLDER"], "pie.png")
            plt.savefig(pie_path)
            plt.close()
            charts.append(pie_path)

            # ✅ Bar Chart
            plt.figure(figsize=(8,5))
            category_summary.plot(kind="bar", color="skyblue")
            plt.title("Expenses by Category")
            plt.ylabel("Amount")
            bar_path = os.path.join(app.config["CHART_FOLDER"], "bar.png")
            plt.savefig(bar_path)
            plt.close()
            charts.append(bar_path)

            # ✅ Line Chart (expenses over time if Date column exists)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                time_summary = df.groupby("Date")["Amount"].sum()
                plt.figure(figsize=(8,5))
                time_summary.plot(kind="line", marker="o")
                plt.title("Expenses Over Time")
                plt.ylabel("Amount")
                line_path = os.path.join(app.config["CHART_FOLDER"], "line.png")
                plt.savefig(line_path)
                plt.close()
                charts.append(line_path)

    return render_template("index.html", charts=charts)

if __name__ == "__main__":
    app.run(debug=True)
