# Application Layer
from flask import Flask

app = Flask(__name__) # create app instance

@app.route("/") # at the end point /
def hello():    # call method hello
    return "Hello world!"

@app.route("/<name>") # at the end point /<name>
def hello_name(name): # call method hello_name
    return "Hello " + name

# routes refer to the url
# for instance, the name function will run when the url is http://localhost:5000/[insert name]
# and will return what follows the 5000/ (aka the name)

if __name__ == "__main__":
    app.run(debug=True)