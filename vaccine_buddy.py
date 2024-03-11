from flask import Flask, render_template
import pymongo
from datetime import datetime
from datetime import timedelta

# flask app settings
app = Flask(__name__)

# Timezone (GMT) constant used to adjust the time zone for page update timestamps.
TIMEZONE = -5

# Mongo database client connection settings
client = pymongo.MongoClient("mongodb+srv://vaccine_buddy_user:Br4bODkOhkhvcOU0@cluster0.2efzlbn.mongodb.net/?retryWrites=true&w=majority")
mydb = client["vaccine_buddy"]  # Name of the database
mycol = mydb["inventory"]  # Name of the collection


def renderlist(inputobj: object) -> str:  # Renders a mongo database query object as html table. Returns a string containing the HTML table.
    inputdict = list(inputobj)  # Convert the inputted mongo query object into a list so we can access the values a bit easier.
    results_output_html = "<table>\n\t<tr>\n\t\t<th>Manufacturer</th>\n\t\t<th>Lot Number</th>\n\t\t<th>Expiration Date</th>\n\t</tr>"  # Start the table HTML with headers.
    for record in inputdict:  # Loop through the array of dictionaries and use their contents to build a string containing the rows of the HTML table for output.
        results_output_html += "\t<tr>\n\t\t<td>" + str(record["manufacturer"]) + "</td>\n\t\t<td>" + record["lotNum"] + "</td>\n\t\t<td>" + record["expDate"].strftime('%m-%d-%y') + "</td>\n\t</tr>\n"
    results_output_html += "</table>"  # Concatenate the close table tag to the html now that we are done adding rows.
    return results_output_html


#  Custom query string: mongoquerycustom("Astra Zeneca", datetime.strptime("03-13-2024", "%m-%d-%Y"), "MJYOF-01-454422")
def mongoquerycustom(manu: str, expdate: datetime, lotnum: str) -> object:  # Run a query to find a single item matching the specified criteria. Returns the results as a mongo query object.
    mongo_query_results = mycol.find({"expDate": expdate, "manufacturer": manu, "lotNum": lotnum})
    return mongo_query_results


def mongodelete(deleteobject: object) -> bool:  # Deletes the documents contained in a query object from the database.
    deletelist = list(deleteobject)
    success = False
    return success


def mongoqueryweeks(weeks_amt: int) -> object:  # Run a query to show all of the items in the database that are expiring in a defined number of weeks. Returns the results as a mongo query object.
    querydepth = datetime.now() + timedelta(weeks=weeks_amt)  # Calculate the date <weeks_amt> weeks from today's date so we can use it as the max date for the query.
    mongo_query_results = mycol.find({"$and": [{"expDate": {"$lt": querydepth}}, {"expDate": {"$gt": datetime.now()}}]}, projection={"_id": 0}).sort("expDate", 1)
    return mongo_query_results


def mongoqueryall() -> object:  # Run a query to show all of the items in the database. Returns the results as a mongo query object.
    mongo_query_results = mycol.find({}, projection={"_id": 0}).sort("expDate", 1)  # Query all rows in database, order by expDate descending, returns the results as a mongo query object.
    return mongo_query_results


def mongoqueryexpired() -> object:  # Run a query to show all of the items that have an expiry date that has already passed. Returns the results as a mongo query object.
    mongo_query_results = mycol.find({"expDate": {"$lt": datetime.now()}}, projection={"_id": 0}).sort("expDate", 1)
    return mongo_query_results


def datetimestamp() -> str:  # Creates a formatted date/time stamp. Adjusted by the TIMEZONE constant.
    date_time_temp = datetime.utcnow() + timedelta(hours=TIMEZONE)
    stamp = date_time_temp.strftime('Updated at: %#H:%#M:%#S - %A, %B %#d %Y')
    return stamp


@app.route("/")  # Displays a list of all vaccines expiring between today and 2 weeks from today.
def weeks2():
    results_output_html = renderlist(mongoqueryweeks(2))
    return render_template("queryresults.html", pagecontent=results_output_html)


@app.route("/weeks4")  # Displays a list of all vaccines expiring between today and 4 weeks from today.
def weeks4():
    results_output_html = renderlist(mongoqueryweeks(4))
    return render_template("queryresults.html", pagecontent=results_output_html)


@app.route("/expired")  # Displays a list of all expired vaccines in the database.
def expired():
    results_output_html = renderlist(mongoqueryexpired())
    return render_template("queryresults.html", pagecontent=results_output_html)


@app.route("/add")  # Displays a form to add a vaccine to the database.
def add():
    add_form = "Add vaccine form goes here"
    return render_template("queryresults.html", pagecontent=add_form)


@app.route("/addresult")  # Displays confirmation of the query to add a vaccine to the database, shows what was added.
def addresult():
    add_result = "Results of the vaccine addition operation"
    return render_template("queryresults.html", pagecontent=add_result)


@app.route("/remove")  # Allows the user to remove either one vaccine, or remove all expired vaccines.
def remove():
    remove_form = "Remove vaccine / Remove all expired form goes here"
    return render_template("queryresults.html", pagecontent=remove_form)


@app.route("/removequeryresult")  # Shows the confirmation screen listing the vaccines to be removed from the database.
def removequeryresult():
    #remove_form_results = renderlist(list(mongoquerycustom(,,,)))
    return render_template("queryresults.html")  # pagecontent=remove_form_results


@app.route("/removeactionfeedback")  # Shows the confirmation on whether the removal of the requested vaccines was successful.
def removeactionfeedback():
    remove_action_results = "Remove action results go here"
    return render_template("queryresults.html", pagecontent=remove_action_results)


@app.route("/showall")  # Shows all of the vaccines in the database.
def showall():
    results_output_html = renderlist(mongoqueryall())
    return render_template("queryresults.html", pagecontent=results_output_html)


if __name__ == "__main__":
    app.run(debug=False)