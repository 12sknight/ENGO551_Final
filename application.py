import os, json

from flask import Flask, session, render_template, request, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from math import sin, cos, sqrt, atan2, pi
import math

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
    water = db.execute("SELECT * FROM water").fetchall()
    parks = db.execute("SELECT * FROM parks").fetchall()
    username=session["username"]

    # get the dog GPS ids and names for the user
    ids = db.execute("SELECT gps_id,dog from  table2 WHERE username=:username",{"username":username}).fetchall()
    ids = list(ids)
    # get the number of dogs that exists for that user
    num = db.execute("SELECT gps_id,dog from  table2 WHERE username=:username",{"username":username}).rowcount
    # loop through dogs
    latest = []
    i = 0
    while i < num:
        id = ids[i][0]
        dog = ids[i][1]
        lastday = db.execute("SELECT max(dte) FROM table3 WHERE gps_id=:gps_id",{"gps_id":id}).fetchone()
        lastday = lastday[0]
        lasttime = db.execute("SELECT max(tme) FROM table3 WHERE (gps_id=:gps_id AND dte=:dte)",{"gps_id":id, "dte":lastday}).fetchone()
        lasttime = lasttime[0]
        lastlat = db.execute("SELECT lat FROM table3 WHERE (gps_id=:gps_id AND dte=:dte AND tme=:tme)",{"gps_id":id, "dte":lastday, "tme":lasttime}).fetchone()
        lastlat = lastlat[0]
        lastlong = db.execute("SELECT lng FROM table3 WHERE (gps_id=:gps_id AND dte=:dte AND tme=:tme)",{"gps_id":id, "dte":lastday, "tme":lasttime}).fetchone()
        lastlong = lastlong[0]
        # to pass to the usermap
        latest.append([id,dog,lastlat,lastlong,lastday,lasttime])
        i+=1

    return render_template("usermap.html", water=water, parks=parks, username=username, latest=latest)

@app.route("/history",methods=["GET","POST"])
def history():
    def sphere_distance(lat1, long1, lat2, long2):
        # radius of earth
        R = 6371
        # Converts lat & long to spherical coordinates in radians.
        d2r = pi/180.0

        #latitude
        lat1=lat1*d2r
        lat2=lat2*d2r

        #longitude
        long1 = long1*d2r
        long2 = long2*d2r

        dlat = lat2-lat1
        dlon = long2-long1

        # Compute the spherical distance from spherical coordinates.
        # Haversine formula
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        arc = R * c

        return arc

    if request.method=="POST":
        username=session["username"]
        temp=db.execute("SELECT GPS_ID, dog FROM table2 WHERE username=:username",{"username":username})
        dogs=temp.fetchall()
        date = request.form.get("datepicker")

        dogname = request.form.get("dogs")
        #dogname = "Buddy"

        # perform query on table 2 to get the gps id for that dog name and username
        id = db.execute("SELECT gps_id FROM table2 WHERE (username = :username AND dog = :dogname)", {"username":username,"dogname":dogname}).fetchone()
        id = id[0]
        # perform query on table 3 to get the lat, long, and time values for the dog on the selected day
        h = db.execute("SELECT lat,lng,tme FROM table3 WHERE (dte=:date AND gps_id=:id)", {"date":date,"id":id}).fetchall()
        num = db.execute("SELECT lat,lng,tme FROM table3 WHERE (dte=:date AND gps_id=:id)", {"date":date,"id":id}).rowcount
        history = list(h)

        distance = 0
        i = 0
        # loop to calculate each distance and add all together
        if num > 1:
            while i < (num-1):
                dist = sphere_distance(history[i][0],history[i][1],history[i+1][0],history[i+1][1])
                distance = distance + dist
                i+=1
            distance = round(distance,2)

        return render_template("history.html", username=username, dogs=dogs, history=history, dogname=dogname, date=date, distance=distance)

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

# API
@app.route("/api/<gps_id>/<date>", methods=['GET'])
def api(gps_id,date):
    # function to calculate the distance between two lat and long values
    def sphere_distance(lat1, long1, lat2, long2):
        # radius of earth
        R = 6371
        # Converts lat & long to spherical coordinates in radians.
        d2r = pi/180.0

        #latitude
        lat1=lat1*d2r
        lat2=lat2*d2r

        #longitude
        long1 = long1*d2r
        long2 = long2*d2r

        dlat = lat2-lat1
        dlon = long2-long1

        # Compute the spherical distance from spherical coordinates.
        # Haversine formula
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance

    # return an error if the gps_id does not exist in our database
    exist = db.execute("SELECT * FROM table3 WHERE gps_id=:gps_id",{"gps_id":gps_id})
    if exist.rowcount==0:
        return render_template("error.html", message="GPS ID not found.")

    # use gps_id to get the name of the dog and all the location data from the date
    dog = db.execute("SELECT dog from table2 WHERE gps_id=:gps_id",{"gps_id":gps_id}).fetchone()
    dog = dog[0]
    locations = db.execute("SELECT lat,lng,tme from table3 WHERE (gps_id=:gps_id AND dte=:dte)",{"gps_id":gps_id,"dte":date}).fetchall()
    locations = list(locations)
    num = db.execute("SELECT * from table3 WHERE (gps_id=:gps_id AND dte=:dte)",{"gps_id":gps_id,"dte":date}).rowcount
    # ensure entries are sorted by time
    locations.sort(key=lambda x: x[2])

    # loop to calculate each distance and add all together
    if num > 1:
        i = 0;
        distance = 0
        while i < (num-1):
            dist = sphere_distance(locations[i][0],locations[i][1],locations[i+1][0],locations[i+1][1])
            distance = distance + dist
            i+=1
        distance = round(distance,2)
    else:
        distance = []
    # object to return
    data = {
        "name": dog,
        "date": date,
        "distance": distance
    }
    return(jsonify(data))

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
