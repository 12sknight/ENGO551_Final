import os, json

from flask import Flask, session, render_template, request, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    #Main page = map page
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():

    #If user is logging in
    if request.method=="POST":
        #get username and password from form
        uname=request.form.get("username")
        passw=request.form.get("password")
        temp=db.execute("SELECT * FROM table1 WHERE username = :username AND pass = :pass",{"username":uname, "pass":passw})
        temp2=temp.fetchall()
        #start a session for the user
        session["username"]=uname

        #see if password and username are correct
        if db.execute("SELECT * FROM table1 WHERE username = :username AND pass = :pass",{"username":uname, "pass":passw}).rowcount >1:
            return render_template("error.html", message="Username or Password is not correct")
        else:
            return redirect("/add")
    else:
        return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    #if the user is inputing data
    if request.method=="POST":
        #Check if passwords match
        passw=request.form.get("password")
        cpass=request.form.get("confpassword")
        try:
            passw==cpass
        except ValueError:
            return render_template("error.html", message="Passwords Don't Match")

            #See if username exsist, if not add user to data base
        uname=request.form.get("username")
        if db.execute("SELECT * FROM table1 WHERE username = :username",{"username":uname}).rowcount >0:
            return render_template("error.html", message="Username is already taken")
        db.execute("INSERT INTO table1 (username, pass) VALUES (:uname, :passw)",
                {"uname": uname,"passw": passw})
        db.commit()

        return redirect("/login")
    #if user method is GET
    else:
        return render_template("signup.html")

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        username=session["username"]
        print(username)
        GPS_ID=request.form.get("gpsid")
        dog=request.form.get("dog")

        #See if GPS ID exist already
        if db.execute("SELECT * FROM table2 WHERE GPS_ID = :GPS_ID",{"GPS_ID":GPS_ID}).rowcount>0:
            return render_template("error.html",message="GPS ID Already Exist")

        else:
            db.execute("INSERT INTO table2 (GPS_ID,dog,username) VALUES (:GPS_ID,:dog,:username)",
                {"GPS_ID":GPS_ID,"dog":dog,"username":username})
            db.commit()
        return redirect("/add")

    else:
        username=session["username"]
        temp=db.execute("SELECT GPS_ID, dog FROM table2 WHERE username=:username",{"username":username})

        dogs=temp.fetchall()

            #return render_template("doglist.html", dogs=dogs)
        return render_template("add.html", dogs=dogs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
