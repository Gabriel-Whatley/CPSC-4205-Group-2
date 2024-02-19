from flask import Flask, render_template

# flask app settings
app = Flask(__name__)


@app.route("/")
def weeks2():
    return render_template("pagetemplate.html")


@app.route("/weeks4")
def weeks4():
    return render_template("pagetemplate.html")


@app.route("/expired")
def expired():
    return render_template("pagetemplate.html")


@app.route("/add")
def add():
    return render_template("pagetemplate.html")


@app.route("/remove")
def remove():
    return render_template("pagetemplate.html")


@app.route("/all")
def all():
    return render_template("pagetemplate.html")


if __name__ == "__main__":
    app.run(debug=True)