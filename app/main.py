from flask import Flask, redirect
 
app = Flask(__name__)
 
@app.route("/")
def home_view():
        return """<h1>Hello Valley and Vivi, how are you?</h1>
        <h3>I am gay boy</h3>"""

@app.route("/favicon.ico")
def reroute():
    return redirect("https://flask-web1738.herokuapp.com/", code=302)