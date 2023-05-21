from flask import Flask

app = Flask("HelloWorld")


@app.route("/")
def hello():
    return "Hello"


app.run(host="0.0.0.0")
