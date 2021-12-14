from flask import Flask
 
app = Flask(__name__)
 
@app.route("/")
def home_view():
        return "<h1>Wassup nerd, serving it up like Federer from Flask</h1>"