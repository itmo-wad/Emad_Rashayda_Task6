from flask import Flask, render_template,request,send_from_directory,redirect,session,flash
import re
import pymongo
import os

client = pymongo.MongoClient(os.environ.get('MONGODB_URI', None))
db = client.get_default_database()
users = db["users"]
users.create_index("username")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/upload'
app.secret_key = "super secret key"

    
def add_user_to_db(username,password):
      users.insert({
            "username": username,
            "password": password,
            "avatar"  : ""
        })
    
def check_user_in_db(username):
    # user = users.find({"username":username})
    user = users.find_one({"username":username})
    if user :        
       
        return True
		

def check_pass_in_db(username,password):
        user=users.find_one({"username":username})
        if user["password"] == password:
            return True

			
def get_avatar(username):
        user=users.find_one({"username":username})
        return user["avatar"] 
		
		
@app.route('/', methods=['Get','POST'])
@app.route('/cabinet', methods=['Get','POST'])

def index():

      if not session.get('logged_in'):
           return redirect("/login", code=302)
      
      else:
        username = session.get('username')   
        
        
        if request.method == 'POST':
              if request.referrer.endswith('login'):
                  return redirect("/cabinet")
				  
		if request.files['file'].filename == "":
                      flash('Name is blank_')
                      return redirect("/cabinet")
					  
		av = request.files['file']
                avatar = os.path.join(app.config['UPLOAD_FOLDER'], av.filename)
                av.save(avatar)
                update_avatar(username,avatar)
                flash('avatar saved!')
				
         file = get_avatar(username)                      
        return render_template('cabinet.html',file=file)
		              
 @app.route('/uploads/<image_name>')
def upload_file(image_name):
       return send_from_directory(app.config['UPLOAD_FOLDER'],image_name)          
          
@app.route('/login', methods=['GET','POST'])
def do_admin_login():
    
    if request.method=='GET':
        session['logged_in'] = False
          return render_template('login.html')   
    
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if "email" not in request.form :
                if check_user_in_db(username):
                    if check_pass_in_db(username, password):
                        session['logged_in'] = True
						session['username'] = username
                    else :
                        flash('Password incorrect, try again')
                else:
                    flash('User not found')
                return index()    
            
        else:
       
             if check_user_in_db(username) :
                     flash('Username already registered!')
                     session['logged_in'] = False
                     return do_reg()
             else:
                 add_user_to_db(username, password)
                 session['logged_in'] = False
                 return index()
                    

 
@app.route('/register')
def do_reg():
    return render_template('register.html')    

     
@app.route('/static/<image_name>')
def index2(image_name):
       return send_from_directory('static/img',image_name)
       

@app.route('/static/<path:path>')
def index3(path):
     return app.send_static_file(path)

  
if __name__ == '__main__':

    app.run( port='5000',threaded=True)