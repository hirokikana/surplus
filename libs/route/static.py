from application import app

from bottle import route,template,static_file

@app.route('/')
def index():
    return template('index', title="TOP")

@app.route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root="./static")
