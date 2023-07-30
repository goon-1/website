from flask import Flask, render_template
import sqlite3

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR

from flask import request, redirect, url_for

from sqlalchemy.orm import declarative_base  

from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils.functions import database_exists

#============================================================#
#================ making a special access code===============#
#============================================================#

import csv
import random

  
with open('accesscodes.csv', 'w') as csvfile:
    accesscodewriter = csv.writer(csvfile, delimiter=' ')
    accesscodewriter.writerow(str(random.randint(1, 99999)))

with open('accesscodes.csv') as accesscodes:
    accesscodereader = csv.reader(accesscodes, delimiter=' ')
    last_line = str(accesscodes.readlines())
  
#============================================================#
#=================making a special access code===============#
#============================================================#

# starting sql alchemy stuff
Base = declarative_base()


#======================Making a user class=======================
class User(Base):
  __tablename__ = "users"

  userID = Column("userID", Integer, primary_key=True, autoincrement=True)
  userfirstName = Column("userfirstName", String)
  userlastName = Column("userlastName", String)
  userPassword = Column("userPassword", String)

  

  def __init__(self, userID, userfirstName, userlastName, userPassword):
    self.userID = userID
    self.userfirstName = userfirstName
    self.userlastName = userlastName
    self.userPassword = userPassword

  def get_ID(self):
    return self.userID

  def get_firstName(self):
    return self.userfirstName

  def get_lastName(self):
    return self.userlastName

  def get_Password(self):
    return self.userPassword


  def __repr__(self):
    return f"{self.userfirstName} {self.userlastName}s user ID is {self.userID}"


#=======================Making the drone class=======================
class Drone(Base):
  __tablename__ = "drones"

  droneID = Column("droneID", Integer, primary_key=True)
  dronetype = Column("dronetype", String)
  dronename = Column("dronename", String)
  owner = Column(Integer, ForeignKey("users.userID"))
  

  def __init__(self, droneID, dronetype, dronename, owner):
    self.droneID = droneID
    self.dronetype = dronetype
    self.dronename = dronename
    self.owner = owner

  def __repr__(self):
    return f"{self.droneID}) is the ID. {self.dronetype} is the type of drone e.g. tinywhoop, racing, freestyle, cinematic. {self.dronename} is the name of the drone."


#===============================================================================#


db_url = "sqlite:///drones.db" #variable for database URL
engine = create_engine(db_url, echo=True)

#Create the database or use existing one
if database_exists(db_url):
  print(f"The {db_url} database already exists so we don't need to add any more data right now.")

else:
  print("Couldn't find the drones.db database so we'll make a new one with an admin account and drone. Password is 'een glish'")

  #============create a session============#
  Base.metadata.create_all(bind=engine)
  Session = sessionmaker(bind=engine)
  session = Session()
  #============create a session============#

  #----------------------------------------#
  
  #============commit an admin!============#
  admin = User(23001,"admin", "", "een glish")
  session.add(admin)
  session.commit()
  #============commit an admin!============#

  #----------------------------------------#
  
  #============commit a drone!!============#
  drone1 = Drone(23001, "Cinerat", "admin drone", admin.userID)
  session.add(drone1)
  session.commit()
  #============commit a drone!!============#

  print("database data added")




#================creating all of the routes for the website================#

app = Flask(__name__)

# route you are directed to when loading up the site for the first time
@app.route('/')
def root():
  return render_template('home.html', page_title='HOME')

@app.route('/lightmode')
def lightmode():
  return render_template('lightmode.html', page_title='LIGHTMODE')
  
# about route - pretty boring
# just a copy of the home page with more information
@app.route('/about')
def about():
    return render_template('about.html', page_title='ABOUT')

# showcasing all drones page
@app.route('/all_drones')
def all_drones():

    #===connecting and fetching data from the drones.db database===#
    conn = sqlite3.connect('drones.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM drones ORDER BY droneID ASC;')
    
    drones = cur.fetchall()
    print(drones)
    conn.close()
    print("Drones have been fetched")
    #===connecting and fetching data from the drones.db database===#
  
    return render_template('all_drones.html', page_title='ALL DRONES', drones=drones)

# shows all of the users page
@app.route('/all_users')
def all_users():

    conn = sqlite3.connect('drones.db')
    cur = conn.cursor()
    cur.execute('SELECT userID, userfirstName, userlastName FROM users ORDER BY userID ASC;')

    users = cur.fetchall()
    conn.close()
    return render_template('all_users.html', page_title='ALL USERS', users=users)

# adding a drone page (very fancy, good job)

@app.route('/add_drone', methods=['POST', 'GET'])  

def add_drone():
  if request.method == "POST":

    # requesting data from the form we did on add_drone.html
    drone_id = request.form.get("dID")
    drone_type = request.form.get("dTYPE")
    drone_name = request.form.get("dNAME")
    user_id = request.form.get("uNAME")

    # making a session (also pretty fancy, i don't know how it works)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    drone_id = int(drone_id)

    # instantiating a new Drone object with the data from the form
    newDrone = Drone(drone_id, drone_type, drone_name, user_id)

    #adding the newDrone to the session then committing it to drones.db
    session.add(newDrone)
    session.commit()
    print("drone added")
    
  else:
    # didn't work 
    print("Could not add drone")
  return render_template("add_drone.html")
    

@app.errorhandler(404)
# r.i.p. that page that could not be found
def page_not_found(e):
   return render_template("404.html")

#-----------------------------------------------

# this admin route is the coolest because you can access admin_dashboard and see everything.
# this includes 
# - viewing the special access codes for making a new users
# - editing and removing users,
# - re-generating the special codes

@app.route('/admin_dashboard')
def admin_dashboard():
  with open('accesscodes.csv') as accesscodes:
    last_line = str(accesscodes.readlines())
    
  # yikes, that's a pretty ugly return statement - it returns the html page, the page title
  # and an awful variable called last_line that holds the special access code.
  return render_template('admin_dashboard.html', page_title='admin_dashboard', last_line=last_line.replace(" ", "").replace("'", "").replace("[", "").replace("]", "").replace("n", "").replace("\\", ""))
  

@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
  if request.method == "POST":

    uID = request.form.get("uID")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    password = request.form.get("password")


    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
      uID = int(uID)
    except ValueError:
      return render_template('add_user.html')

    if uID == '' or fname == '' or lname == '' or password == '':
      return render_template('add_user.html')
    else:
      pass
    newUser = User(uID, fname, lname, password)

    session.add(newUser)
    session.commit()
    print("user added")
    
  else:
    print("Could not add drone")
  return render_template("add_user.html")

# checks what user id the user puts in, and then searches for that user id in the drones.db file.
# If there is a user, it then checks user.password and sees if that matches up with whatever password the user has set.


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
  
    if request.method == 'POST':
      # this variable is the userid the user put in
      formID = request.form['userid']
      
      Base.metadata.create_all(bind=engine)
      Session = sessionmaker(bind=engine)
      session = Session()
      # getting input with ssn = ssn in HTML form
      userID = formID
      print("userid requested is ... " + userID)
      try:
       userID = int(userID)
      except ValueError:
        return render_template('login.html')
      
      user = session.query(User).filter(User.userID == userID).first()

      try:
        if request.form.get("password") == user.get_Password():
          return render_template('add_drone.html')
        else:
          return render_template('login.html', error=error)
      except (ValueError, AttributeError):
        return render_template('login.html')
    
    return render_template('login.html', error=error)




@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    error = None
  
    if request.method == 'POST':
      # this variable is the userid the user put in
      formID = request.form['userid']
      
      Base.metadata.create_all(bind=engine)
      Session = sessionmaker(bind=engine)
      session = Session()
      # getting input with ssn = ssn in HTML form
      userID = formID
      print("userid requested is ... " + userID)

      results=session.query(Drone, User).filter(Drone.owner == User.userID).all() 
      print("Things and owners are ")
      print(results)
      
      try:
        userID = int(userID)
      except ValueError:
        return render_template('sign_in.html')
        
      try:
        user = session.query(User).filter(User.userID == userID).first()
      except AttributeError:
        print("that shit is not going to work my g")
        
      try:
        if user.get_ID() == 23001 and request.form.get("password") == user.get_Password():
          with open('accesscodes.csv') as accesscodes:
            last_line = str(accesscodes.readlines())
      except AttributeError:
        print("that shit is not going to work my g")

      try:
        return render_template('admin_dashboard.html', page_title='admin_dashboard', last_line=last_line.replace(" ", "").replace("'", "").replace("[", "").replace("]", "").replace("n", "").replace("\\", ""))
      except UnboundLocalError:
        return render_template('sign_in.html')
        
  
      else:
        if request.form.get("password") == user.get_Password():
          return render_template('dashboard.html', results)
        else:
          return render_template('sign_in.html', error=error)
    
    return render_template('sign_in.html', error=error)




# I'm not quite sure why I made this, ask me later - I was in a $ coding frenzy $
@app.route('/accesscode', methods=['GET', 'POST'])
def accesscode():
  if request.method == 'POST':

     #=============reads the current access code============#
    with open('accesscodes.csv') as accesscodes:
      da_code = str(accesscodes.readlines())
     #=============reads the current access code============#

    if request.form.get("code") == da_code.replace(" ", "").replace("'", "").replace("[", "").replace("]", "").replace("n", "").replace("\\", ""):
    
      #===resets the access code so you cant use it again===#
      with open('accesscodes.csv', 'w') as csvfile:
        accesscodewriter = csv.writer(csvfile, delimiter=' ')
        accesscodewriter.writerow(str(random.randint(10000, 99999)))
      #===resets the access code so you cant use it again===#
        
      return render_template('add_user.html')
    else:
      return render_template('accesscode.html')
  else:
    return render_template('accesscode.html')

  return render_template('accesscode.html')
      

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=8080)