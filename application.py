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
    #Main page = map page without user being logged in
    water = db.execute("SELECT * FROM water").fetchall()
    parks = db.execute("SELECT * FROM parks").fetchall()
    return render_template("index.html", water=water, parks=parks)

@app.route("/login", methods=["GET","POST"])
def login():

    #If user is logging in
    if request.method=="POST":
        #get username and password from form
        uname=request.form.get("username")
        passw=request.form.get("password")
        #start a session for the user
        session["username"]=uname

        #see if password and username are correct
        if db.execute("SELECT * FROM table1 WHERE username = :username AND pass = :pass",{"username":uname, "pass":passw}).rowcount >1:
            return render_template("error.html", message="Username or Password is not correct")
        #If they are correct go to /add route
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
        #Redirect to /login
        return redirect("/login")
    #if user method is GET
    else:
        return render_template("signup.html")

@app.route("/usermap",methods=["GET","POST"])
def usermap():
    #***ZOE add last gps location from dog(s) for user logged in***

    water = db.execute("SELECT * FROM water").fetchall()
    parks = db.execute("SELECT * FROM parks").fetchall()
    username=session["username"]
    return render_template("usermap.html", water=water, parks=parks, username=username)

@app.route("/history",methods=["GET","POST"])
def history():
    if request.method=="POST":
        username=session["username"]
        temp=db.execute("SELECT GPS_ID, dog FROM table2 WHERE username=:username",{"username":username})
        dogs=temp.fetchall()
        date = request.form.get("datepicker")

        #dogname = request.form.get("dogpicker")
        dogname = "Buddy"

        # perform query on table 2 to get the gps id for that dog name and username
        id = db.execute("SELECT gps_id FROM table2 WHERE (username = :username AND dog = :dogname)", {"username":username,"dogname":dogname}).fetchone()
        id = id[0]
        # perform query on table 3 to get the lat, long, and time values for the dog on the selected day
        h = db.execute("SELECT lat,lng,tme FROM table3 WHERE (dte=:date AND gps_id=:id)", {"date":date,"id":id}).fetchall()
        history = list(h)

        return render_template("history.html", username=username, dogs=dogs, history=history, dogname=dogname, date=date)

    if request.method=="GET":
        #this is used for when they first navigate to the page and no
        #history is displayed.
        username=session["username"]
        temp=db.execute("SELECT GPS_ID, dog FROM table2 WHERE username=:username",{"username":username})
        dogs=temp.fetchall()
        return render_template("history.html", username=username, dogs=dogs)


@app.route("/add",methods=["GET","POST"])
def add():
    #If user wants to add a dog
    if request.method=="POST":
        username=session["username"]

        GPS_ID=request.form.get("gpsid")
        dog=request.form.get("dog")

        #See if GPS ID exist already
        if db.execute("SELECT * FROM table2 WHERE GPS_ID = :GPS_ID",{"GPS_ID":GPS_ID}).rowcount>0:
            return render_template("error.html",message="GPS ID Already Exist")
        #add to dog table
        else:
            db.execute("INSERT INTO table2 (GPS_ID,dog,username) VALUES (:GPS_ID,:dog,:username)",
                {"GPS_ID":GPS_ID,"dog":dog,"username":username})
            db.commit()

        #Redirect to the same route to update dog list
        return redirect("/add")

    else:
        #Get all the dog info corresponding to the session username
        username=session["username"]
        temp=db.execute("SELECT GPS_ID, dog FROM table2 WHERE username=:username",{"username":username})

        dogs=temp.fetchall()

            #display dog info as a table
        return render_template("add.html", dogs=dogs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
