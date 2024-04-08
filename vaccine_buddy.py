from flask import Flask, render_template, request, make_response
import pymongo
from datetime import datetime
from datetime import timedelta
from sessionmanager import SessionManager
import vaccine_generator


# flask app settings
app = Flask(__name__)

# Timezone (GMT) constant used to adjust the time zone for page update timestamps.
TIMEZONE = -5

# Mongo database client connection settings
client = pymongo.MongoClient("mongodb+srv://vaccine_buddy_user:Br4bODkOhkhvcOU0@cluster0.2efzlbn.mongodb.net/?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
mydb = client["vaccine_buddy"]  # Name of the database
mycol = mydb["inventory"]  # Name of the collection

# Create a new sessionmanager object to track a maximum of 20 removal query sessions.
sessionmanager = SessionManager(20)


def renderlist(inputobj: pymongo.cursor.Cursor) -> str:
    """Renders a mongo database query results object as html table.

    :param inputobj: Results of a pymongo query.

    :returns: html of the table, ready for injection in the webpage"""
    inputlist = list(inputobj)  # Convert the inputted mongo query object into a list so we can access the values a bit easier.
    if len(inputlist) > 0:
        results_output_html = "<table>\n\t<tr>\n\t\t<th>Manufacturer</th>\n\t\t<th>Lot Number</th>\n\t\t<th>Expiration Date</th>\n\t</tr>"  # Start the table HTML with headers.
        for record in inputlist:  # Loop through the array of dictionaries and use their contents to build a string containing the rows of the HTML table for output.
            results_output_html += "\t<tr>\n\t\t<td>" + str(record["manufacturer"]) + "</td>\n\t\t<td>" + record["lotNum"] + "</td>\n\t\t<td>" + record["expDate"].strftime('%m-%d-%y') + "</td>\n\t</tr>\n"
        results_output_html += "</table>"  # Concatenate the close table tag to the html now that we are done adding rows.
    else:
        results_output_html = "<table><tr><td>Our search of the database did not return any results.</td></tr></table>"
    return results_output_html


def mongoquerycustom(manu_name: str, exp_date: str | datetime, lot_num: str) -> pymongo.cursor.Cursor:
    """Run a query to find a specific item in the database.

    :param manu_name: manufacturer name.
    :param exp_date: date of vaccine expiration, strings must be formatted 'YYYY-MM-DD'
    :param lot_num: lot number of the vaccine

    :returns: The results as a mongo query object."""
    if type(exp_date) is "string":
        exp_date = datestrconvert(exp_date)
    mongo_query_results = mycol.find({"manufacturer": manu_name, "expDate": exp_date, "lotNum": lot_num})
    return mongo_query_results


def mongoqueryweeks(weeks_amt: int) -> pymongo.cursor.Cursor:
    """Run a query to show all of the items in the database that are expiring in a defined number of weeks. Returns the results as a mongo query object.

    :param weeks_amt: number of weeks in the future to query.

    :returns: The results as a mongo query object."""
    querydepth = datetime.now() + timedelta(weeks=weeks_amt)  # Calculate the date <weeks_amt> weeks from today's date so we can use it as the max date for the query.
    mongo_query_results = mycol.find({"$and": [{"expDate": {"$lt": querydepth}}, {"expDate": {"$gt": datetime.now()}}]}, projection={"_id": 0}).sort("expDate", 1)
    return mongo_query_results


def mongoqueryall() -> pymongo.cursor.Cursor:
    """Run a query to show all of the items in the database. Returns the results as a mongo query object.

    :returns: The results as a mongo query object."""
    mongo_query_results = mycol.find({}, projection={"_id": 0}).sort("expDate", 1)  # Query all rows in database, order by expDate descending, returns the results as a mongo query object.
    return mongo_query_results


def mongoqueryexpired() -> pymongo.cursor.Cursor:
    """Runs a mongodb query to show all of the items that have an expiry date that has already passed.

    :returns: The results as a mongo query object."""
    mongo_query_results = mycol.find({"expDate": {"$lt": datetime.now()}}, projection={"_id": 0}).sort("expDate", 1)
    return mongo_query_results


def datetimestamp() -> str:
    """Creates a formatted date/time stamp. Adjusted by the TIMEZONE constant.

    :returns: formatted string containing the current time and date."""
    date_time_temp = datetime.utcnow() + timedelta(hours=TIMEZONE)
    return date_time_temp.strftime('Updated at: %#H:%#M:%#S - %A, %B %#d %Y')


def datestrconvert(date_str: str) -> datetime:
    """Converts date string from HTML form to datetime object format.

    :param date_str: String of the format YYYY-MM-DD.

    :returns: datetime:datetime object containing the date"""
    return datetime.strptime(date_str, "%Y-%m-%d")


@app.route("/")  # Displays a list of all vaccines expiring between today and 2 weeks from today.
def weeks2():
    time_stamp = datetimestamp()
    results_output_html = renderlist(mongoqueryweeks(2))
    return render_template("queryresults.html", pagecontent=results_output_html, timestamp=time_stamp)


@app.route("/weeks4")  # Displays a list of all vaccines expiring between today and 4 weeks from today.
def weeks4():
    time_stamp = datetimestamp()
    results_output_html = renderlist(mongoqueryweeks(4))
    return render_template("queryresults.html", pagecontent=results_output_html, timestamp=time_stamp)


@app.route("/expired")  # Displays a list of all expired vaccines in the database.
def expired():
    time_stamp = datetimestamp()
    results_output_html = renderlist(mongoqueryexpired())
    return render_template("queryresults.html", pagecontent=results_output_html, timestamp=time_stamp)


@app.route("/add")  # Displays a form to add a vaccine to the database.
def add():
    add_form = "Add vaccine form goes here"
    return render_template("addform.html", pagecontent=add_form)


@app.route("/addresult", methods=['POST'])  # Displays confirmation of the query to add a vaccine to the database, shows what was added.
def addresult():
    manu_name = request.form.get('manu_name')  # Get the data values from the form on the previous page and store them in variables.
    exp_date = datestrconvert(request.form.get('exp_date'))
    lot_no = request.form.get('lot_no')
    mycol.insert_one({"manufacturer": manu_name, "lotNum": lot_no, "expDate": exp_date})  # Generate and run the query to add the vaccine.
    add_result = renderlist(mongoquerycustom(manu_name, exp_date, lot_no))
    return render_template("queryresults.html", pagecontent=add_result)


@app.route("/remove")  # Allows the user to remove either one vaccine, or remove all expired vaccines.
def remove():
    return render_template("removeform.html")


@app.route("/removequeryresult", methods=['POST'])  # Shows the confirmation screen listing the vaccines to be removed from the database.
def removequeryresult():
    session_id = sessionmanager.newsession()
    match request.form.get('submittype'):  # decide what query to run based on the value of the submit button clicked on the previous page.
        case "Remove Single":  # Remove a single vaccine
            manu_name = request.form.get('manu_name')  # Get the data values from the form on the previous page and store them in variables.
            exp_date = request.form.get('exp_date')
            lot_no = request.form.get('lot_no')
            sessionmanager.setquery(session_id, manu_name, exp_date, lot_no)  # Store the values in the sessionmanager tied to the session ID
            query_result = mongoquerycustom(*sessionmanager.getquery(session_id))  # Unpack the values from the tuple returned by querymanager and use them to run a query so we can render a result table.
        case "Remove All Expired":  # Remove all of the expired vaccines.
            sessionmanager.setquery(session_id)  # Set all query values to None to indicate remove all query type.
            query_result = mongoqueryexpired()  # Run the expired vaccines query
    remove_form_results = renderlist(query_result)  # Render the query result as HTML
    resp = make_response(render_template("removeresults.html", pagecontent=remove_form_results))  # build a response with the render template.
    resp.set_cookie("sessionmanagerID", session_id)  # set a cookie in the user's browser with the session_id during the response.
    return resp


@app.route("/removeactionresult", methods=['POST'])  # Shows the confirmation on whether the removal of the requested vaccines was successful.
def removeactionresult():
    session_id = request.cookies.get("sessionmanagerID")  # Get the session ID from the browser cookie.
    manu_name, exp_date, lot_no = sessionmanager.getquery(session_id)  # Get the query values from the sessionmanager.
    match manu_name, exp_date, lot_no:
        case None, None, None:  # Case for remove all expired, no options present.
            result = mycol.delete_many({"expDate": {"$lt": datetime.now()}})  # Delete everything that is expired.
        case _:  # For all other values set query type "remove single"
            result = mycol.delete_many({"manufacturer": manu_name, "expDate": exp_date, "lotNum": lot_no})  # Run the deletion operation.
    remove_action_results = "Succesfully removed {0} entries from the database".format(result.deleted_count)  # Display output of how many records were deleted.
    return render_template("queryresults.html", pagecontent=remove_action_results)


@app.route("/showall")  # Shows all of the vaccines in the database.
def showall():
    time_stamp = datetimestamp()
    results_output_html = renderlist(mongoqueryall())
    return render_template("queryresults.html", pagecontent=results_output_html, timestamp=time_stamp)


@app.route("/reset")  # Reset the database, delete all vaccine entries and re-generate 800 records.
def reset():
    vaccine_generator.resetdatabase(800)
    results_output_html = "Finished resetting database, 800 vaccines generated"
    return render_template("queryresults.html", pagecontent=results_output_html)


if __name__ == "__main__":
    app.run(debug=False)