from flask import Flask,render_template,jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run("0.0.0.0",5000,True)