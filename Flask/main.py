from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# default page
@app.route("/") 
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)