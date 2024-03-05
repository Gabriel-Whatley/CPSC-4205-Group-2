from flask import Flask, render_template
import pymongo
from datetime import datetime
from datetime import timedelta

# flask app settings
app = Flask(__name__)

# Mongo database connection settings
client = pymongo.MongoClient("mongodb+srv://vaccine_buddy_user:Br4bODkOhkhvcOU0@cluster0.2efzlbn.mongodb.net/?retryWrites=true&w=majority")
mydb = client["vaccine_buddy"]  # Name of the database
mycol = mydb["inventory"]  # Name of the collection


def renderlist(inputdict: list) -> str:  # Renders the results of a database query as html.
    results_output_html = "<table>\n\t<tr>\n\t\t<th>Manufacturer</th>\n\t\t<th>Lot Number</th>\n\t\t<th>Expiration Date</th>\n\t</tr>"  #Start the table HTML with headers.
    for record in inputdict:  # Loop through the array of dictionaries and use their contents to build a string containing the rows of the HTML table for output.
        results_output_html += "\t<tr>\n\t\t<td>" + str(record["manufacturer"]) + "</td>\n\t\t<td>" + record["lotNum"] + "</td>\n\t\t<td>" + record["expDate"].strftime('%m-%d-%y') + "</td>\n\t</tr>\n"
    results_output_html += "</table>"  # Concatenate the end the table to the html now that we are done adding rows.
    return results_output_html


def mongoqueryweeks(weeks_amt: int) -> list:  # Run a query to show all of the items in the database that are expiring in a defined number of weeks.
    querydepth = datetime.now() + timedelta(weeks=weeks_amt)  # Calculate the date <weeks_amt> weeks from today's date so we can use it as the max date for the query.
    mongo_query_results = list(mycol.find({"$and": [{"expDate": {"$lt": querydepth}}, {"expDate": {"$gt": datetime.now()}}]}, projection={"_id": 0}).sort("expDate", 1))
    return mongo_query_results  #Returns a list


def mongoqueryall() -> list:  # Run a query to show all of the items in the database.
    mongo_query_results = list(mycol.find({}, projection={"_id": 0}).sort("expDate", 1))  # Query all rows in database, order by expDate descending, returns the results as a list.
    return mongo_query_results  #Returns a list


def mongoqueryexpired() -> list:  # Run a query to show all of the items that have an expiry date that has already passed.
    mongo_query_results = list(mycol.find({"expDate": {"$lt": datetime.now()}}, projection={"_id": 0}).sort("expDate", 1))
    return mongo_query_results  # Returns a list


@app.route("/")
def weeks2():
    results_output_html = renderlist(mongoqueryweeks(2))
    return render_template("pagetemplate.html", pagecontent=results_output_html)


@app.route("/weeks4")
def weeks4():
    results_output_html = renderlist(mongoqueryweeks(4))
    return render_template("pagetemplate.html", pagecontent=results_output_html)


@app.route("/expired")
def expired():
    results_output_html = renderlist(mongoqueryexpired())
    return render_template("pagetemplate.html", pagecontent=results_output_html)


@app.route("/add")
def add():
    return render_template("pagetemplate.html")


@app.route("/remove")
def remove():
    return render_template("pagetemplate.html")


@app.route("/showall")
def showall():
    results_output_html = renderlist(mongoqueryall())
    return render_template("pagetemplate.html", pagecontent=results_output_html)


if __name__ == "__main__":
    app.run(debug=True)