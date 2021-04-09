from flask import Flask, render_template, request, url_for, session, redirect

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/rent')
def rent():
    return render_template('rent.html')


@app.route('/account')
def rent():
    return render_template('account.html')
