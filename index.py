from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, make_response
from src import Acm, Auth
import sqlite3

app = Flask(__name__,static_folder='assets',template_folder='templates')
app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
    return redirect(url_for('home'))

@app.route("/administrator/scrapping")
def administrator_scrapping():
  if Auth('login').check() == True:
    title_page = "Administrator page"
    return render_template("./pages/admin/scrapping.html", content={ "title_page" : title_page})
  else:
    return redirect(url_for('home'))

@app.route("/administrator/scrapping/get-record",methods=["GET"])
def administrator_scrapping_get_record():
  if Auth('login').check() == True:
    keyword = request.args.get('keyword')
    limit = request.args.get('limit')
    actionSearch = Acm(keyword,limit)
    
    result = actionSearch.scrapping()

    return make_response(jsonify({
      'status' : True,
      'data' : result
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False,
    }), 200)

@app.route("/administrator/scrapping/get-total-db",methods=["GET"])
def administrator_scrapping_get_total_db():
  if Auth('login').check() == True:
    keyword = request.args.get('keyword')
    limit = request.args.get('limit')

    conn1 = sqlite3.connect("./database.sqlite")
    records1 = conn1.execute("select * from scrapping_data where (sumber=? AND keyword=?)",('acm',keyword)).fetchall()

    actionSearch = Acm(keyword,limit)
    
    num = actionSearch.getTotal()
    
    if num < int(limit):
      percent = ((len(records1)/int(num))*100)
    else : 
      percent = ((len(records1)/int(limit))*100)

    return make_response(jsonify({
      'status' : True,
      'data' : percent
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False,
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
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
  # remove the username from the session if it is there
  session.pop('login', None)
  flash('Logout Successfuly!')
  return redirect(url_for('administrator'))

if __name__ == '__main__':
  app.run(debug=True)