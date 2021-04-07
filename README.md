# ENGO 551 Final Project
# Dog Tracking and Recreation
## By: Mitchell Brown, Zoe Walsh, Sam Knight

The purpose of this application is to provide 3 solutions:
1) Track your lost dog - Using your dogs last known GPS location
2) Find the closest dog park or water source while on a walk - Using the users phone location
3) Know if your dog has gotten enough exercise - Based on how far they have walked on a given day

As this project is built around the idea of using the app while you are out with your dog, we have made it mobile friendly so it can be used on a smartphone. When you first enter the site, you are presented with a map that contains all dog parks and fountains in Calgary. You have the ability to toggle these layers on and off as well.

### The Main Map:

![Mainmap](/screenshots/1.png)

### Layer View Control

![layercontrol](/screenshots/9.png)

### Dog Park Polygons

![dogparkpoly](/screenshots/14.png)

### Dog Water Fountain Icons

![WaterFountains](/screenshots/2.png)

Users can select the ‘Closest Park’, or ‘Closest Water Fountain’ buttons to instantly get a route from their current location to the nearest park/fountain. 

### Route to the Closest Park

![ClosePark](/screenshots/4.png)

### Route to the Closest Fountain

![CloseFountain](/screenshots/5.png)

New users can sign up, or existing users can log in:

### Sign Up Page

![SignUp](/screenshots/6.png)

### Login Page

![Login](/screenshots/7.png)

Once logged in, users can see all dogs associated with their account, and they have the ability to add more. They can then navigate back to the main map, which will now show their dog(s)’s last GPS location:

### Add Dogs to Account

![AddDogs](/screenshots/8.png)

### Logged in Main Map With Dog Location Display
![ShowDog](/screenshots/10.png)

Logged in users can also query their dog’s past location history by pressing the ‘Dog History’ button. They can select which dog, and the date that they want to query. Then, they will be presented with the dog’s GPS history, distance travelled, and the date/time of the journey. 

### History Options for Each Dog

![DogHistory](/screenshots/12.png)

### View the Dogs Location and Distance History

![WheresDog](/screenshots/13.png)

### API

An API call can be performed by adding \api\<gps_id>\<date> to the url to return a user's dog’s total distance travelled in kilometers on a given day. For example, calling <route>/api/68247412/2021-04-02 will return:

![api](/screenshots/api.png) 



<h3> Mobile Usage </h3>

To use this application on your mobile device, install requirements.txt, which includes pyopenssl. This allows us to run the services with https:// instead of http, so our mobile device will allow the location requests. Then, instead of the `flask run` command, use `flask run --cert=adhoc --host=0.0.0.0`. To access the web application on your mobile device, you will need to connect it to your WiFi, find your WiFi IP address, and enter https://< your IP address >:5000 in your browser. 