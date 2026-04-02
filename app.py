import mysql.connector as cn
import os, hashlib, re,flask, string, random
from flask_cors import CORS
from flask import request, make_response,jsonify

db = cn.connect(
    host="localhost",
    user="william",
    password="säkertlösenord.07"
)

db.autocommit = True

tempCursor = db.cursor()
tempCursor.execute("USE databas2")
tempCursor.close()

app = flask.Flask(__name__,static_folder="static",template_folder="templates")
CORS(app, supports_credentials=True, intercept_exceptions=False)
def genToken(len=128):
    return "".join([random.choice(string.ascii_letters + string.digits) for _ in range(len)]) 

def getUsers():
    tables = []
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM users")
    
    result = cursor.fetchall()
    
    
    cursor.close()
    
    return result
    
def createUser(username:str, password:str, email:str):
    encrypted_password = hashlib.sha256(password.encode("UTF-8")).hexdigest()
    
    cursor = db.cursor()
    token = genToken()
    
    
    cursor.execute(f"INSERT INTO databas2.users (name, email, password, token) VALUES (\"{username}\",\"{email}\",\"{encrypted_password}\", \"{token}\" )")
    
    
    cursor.close()
    return token

def emailExists(email):
    cursor = db.cursor()
    
    cursor.execute(f"SELECT email FROM users WHERE email='{email}'")
    
    if cursor.fetchone():
        print("EXISTS")
        return True
    else:
        print("DOES NOT EXIST")
        return False
    
def passwordValidation(password):
    if re.match(r"^(?=.*[\W_])[a-zA-Z0-9\W_]+$",password):
        return True
    else:
        return False



@app.route("/register", methods=["POST"])
def registerMethod():
    data = flask.request.json
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")
    
    if passwordValidation(password):
        if not emailExists(email):
            token = createUser(name, password, email)
            
            # 1. Create a JSON response instead of a redirect
            # This prevents the double-header collision often caused by 302s
            resp = make_response(jsonify({"success": True}), 200)
            
            # 2. Set the cookie
            # Use samesite='None' and secure=True if frontend/backend are on different domains
            resp.set_cookie("token", token, httponly=True, samesite='Lax')
            return resp
        else:
            return jsonify({"error": "Email exists already"}), 409
    else:
        return jsonify({"error": "Invalid password format"}), 400
    

    
    

@app.route("/login",methods = ["GET","POST"])
def loginMethod():
    if flask.request.method.lower() == "post":
        jsonData = request.json
        email = jsonData["email"]
        passw = jsonData["password"]
        
        encPassw = hashlib.sha256(passw.encode("UTF-8")).hexdigest()
            
        cursor = db.cursor()
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        rowAm = cursor.rowcount
        
        if rowAm == 1:
            row = cursor.fetchone()
            psswd = row["password"]
            if encPassw == psswd:
                token = row["token"]
                resp = flask.make_response(flask.redirect("/"))
                resp.set_cookie("token",token)
                return resp
            else:
                return "Incorrect credentials", 401
        else:
            return "Account not found",404
    else:
        return flask.render_template("login.html")
        

@app.route("/", methods=["GET"])
def home():
    if flask.request.cookies.get("token") != None:
        return flask.render_template("index.html")
    else: 
        return flask.redirect("/login")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
