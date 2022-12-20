from pipes import Template
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, make_response
from src import Acm, Auth, cronjobAcm, Ieee, cronjobIeee, cronjobSpring, Spring
import sqlite3
import math
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz


def runAcmJobs():
  print('running Acm jobs :')
  cronjobAcm.runningJobs()

def runIeeJobs():
  print('running Ieee jobs :')
  cronjobIeee.runningJobs()

def runSpringJobs():
  print('running Spring Link jobs :')
  cronjobSpring.runningJobs()

scheduler = BackgroundScheduler()
scheduler.add_job(func=runAcmJobs, trigger="interval", days=1, next_run_time=datetime.now(pytz.timezone('Asia/Jakarta')), id='acm_job')
scheduler.add_job(func=runIeeJobs, trigger="interval", days=1, next_run_time=datetime.now(pytz.timezone('Asia/Jakarta')), id='ieee_job')
scheduler.add_job(func=runSpringJobs, trigger="interval", days=1, next_run_time=datetime.now(pytz.timezone('Asia/Jakarta')), id='spring_job')
scheduler.start()

app = Flask(__name__,static_folder='assets',template_folder='templates')
app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def home():
  title_page = "Welcome"
  return render_template("./pages/index.html", content={ "title_page" : title_page })

# @app.route("/search",methods=["POST"])
# def home_search():
#   if request.method == "POST":
#     keyword = request.form['search']
#     acm = Acm(keyword)
#   return acm.scrapping()
     
"""
  admin route
"""
@app.route("/administrator")
def administrator():
  if Auth('login').check() == True:
    return redirect(url_for('administrator_index'))
  else:
    title_page = "Login Page"
    return render_template("./pages/admin/login.html", content={ "title_page" : title_page })

@app.route("/process-login",methods=["POST"])
def process_login():
  if request.method == "POST":
    if request.form['username'] == 'admin' and request.form['password'] == 'admin':
      session['login'] = 'administrator'
      flash('Login Successfuly!')
      return redirect(url_for('administrator_index'))

  flash('Invalid credentials!')
  return redirect(url_for('administrator'))

@app.route("/administrator/dashboard")
def administrator_index():
  if Auth('login').check() == True:
    title_page = "Administrator page"
    return render_template("./pages/admin/index.html", content={ "title_page" : title_page})
  else:
    return redirect(url_for('administrator'))

@app.route("/administrator/scrapping")
def administrator_scrapping():
  if Auth('login').check() == True:
    title_page = "Administrator page"

    ## insert to database if not exist
    Acm().insertPass()
    Ieee().insertPass()
    Spring().insertPass()

    conn = sqlite3.connect("./database.sqlite")
    progress_db = conn.execute("select * FROM progress").fetchall()

    return render_template("./pages/admin/scrapping.html", content={ "title_page" : title_page},progress_db=progress_db)
  else:
    return redirect(url_for('administrator'))

# @app.route("/administrator/scrapping/get-record",methods=["POST"])
# def administrator_scrapping_get_record():
#   if Auth('login').check() == True:

#     if request.method == "POST":
#       keyword = request.form['search']
      
#       if len(keyword)>0:
#         conn = sqlite3.connect("./database.sqlite")

#         for x in range(1):
#           _type = ''
#           if x == 0:
#             _type = 'acm'
#             allrecord = Acm().getRecord()
#           elif x == 1:
#             _type = 'ieee'
#           elif x == 2:
#             _type = 'springer link'
#           else:
#             _type = 'google scholar'

#           conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page) values (?, ?, ?, ?, ?)", [_type, 0, allrecord, 0])
#           conn.commit()

#       return redirect(url_for('administrator_scrapping'))
#   else:
#     return redirect(url_for('administrator'))
    
@app.route("/administrator/scrapping/get-total-db",methods=["GET"])
def administrator_scrapping_get_total_db():
  if Auth('login').check() == True:
    conn = sqlite3.connect("./database.sqlite")
    limit = 0
    hasinsert = 0
    break_ = False
    percent = 0

    init = request.args.get('init')
    init = int(init)

    check_0 = conn.execute("select * from progress where (id=?)",[init]).fetchone()
    if check_0 is not None:
      limit = check_0[3]
      check_1 = conn.execute("select * from scrapping_data where (sumber=?)",[check_0[1]]).fetchall()
      hasinsert = len(check_1)
      if check_0[5] == 0:
        break_ = True
      else:
        break_ = False


    percent = 0
    if check_0[1] == 'acm':
      if hasinsert >0 and limit >0 :
        percent = math.ceil(((hasinsert/int(limit))*100))

    if check_0[1] == 'spring':
      if hasinsert >0 and limit >0 :
        percent = math.ceil(((hasinsert/int(limit))*100))

    return make_response(jsonify({
      'status' : True,
      'data' : {
        'percent' : percent,
        'break' : break_,
        'limit': limit,
        'hasinsert':hasinsert
      }
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False,
    }), 200)


@app.route("/administrator/start-stop",methods=["GET"])
def administrator_scrapping_start_top():
  if Auth('login').check() == True:
    conn = sqlite3.connect("./database.sqlite")

    init = request.args.get('init')
    init = int(init)
    value = request.args.get('value')
    value = int(value)

    check = conn.execute("select * from progress where (id=?)",[init]).fetchone()
    if check is not None:
      if value == 0:
        if check[1] == 'acm':
          Acm().updateRecord()

        if check[1] == 'spring':
          Spring().updateRecord()

      if value == 0:
        val = 1
      else:
        val = 0
      conn.execute("UPDATE progress SET start_stop=? WHERE id=?", [val, init])
      conn.commit()

    return make_response(jsonify({
      'status' : True
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False
    }), 200)

@app.route("/administrator/data")
def administrator_data():
  if Auth('login').check() == True:
    
    title_page = "Administrator page"
    conn = sqlite3.connect("./database.sqlite")
    # data = conn.execute("SELECT * FROM scrapping_data Limit ?, ?",('0','10')).fetchall()
    data = conn.execute("SELECT * FROM scrapping_data").fetchall()

    return render_template("./pages/admin/data.html", content={ "title_page" : title_page}, data = data)
  else:
    return redirect(url_for('administrator'))


@app.route('/logout')
def logout():
  # remove the username from the session if it is there
  session.pop('login', None)
  flash('Logout Successfuly!')
  return redirect(url_for('administrator'))

if __name__ == '__main__':
  app.run(debug=False)