from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify

from flask_mysqldb import MySQL

from werkzeug.utils import secure_filename
import os
# import magic
# import urllib.request
from datetime import datetime

app = Flask(__name__, static_folder='static')

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_PORT'] = 3308  # Change this to the new port number
app.config['MYSQL_DB'] = "flaskdb"

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = "ram"


# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# def allowed_file(filename):
#  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fetchUser(email):
    cur = mysql.connection.cursor();
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    return user;


def fetchAllUser():
    cur = mysql.connection.cursor();
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    user = cur.fetchall()
    cur.close()
    return user;


def fetchProfile(email):
    cur = mysql.connection.cursor();
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM profiles WHERE email = %s", (email,))
    profile = cur.fetchone()
    cur.close()
    return profile;


def fetchPosts():
    cur = mysql.connection.cursor();
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    cur.close()
    return posts;


def fetchUserPosts(email):
    cur = mysql.connection.cursor();
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE postedby=%s", (email,))
    posts = cur.fetchall()
    cur.close()
    return posts;


def setLikes(postid):
    cur = mysql.connection.cursor()
    update_query = "UPDATE posts set likes=likes+1 where email=%s"
    cur.execute(update_query, postid, )


def fetchComments(postid):
    cur = mysql.connection.cursor();
    cur.execute("SELECT * FROM comments WHERE postid=%s", (postid,))
    comments = cur.fetchall()
    cur.close()
    return comments


def fetchReq(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT requestes FROM friends WHERE email=%s", (email,))
    req = cur.fetchone()
    print(req[0])
    up = req[0].split(',')
    return up

def fetchFriends(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT friend FROM friends WHERE email=%s", (email,))
    req = cur.fetchone()
    print(req[0])
    friend = req[0].split(',')
    return friend




@app.route("/")
def func():
    return render_template("login.html")


@app.route("/dashboard/<username>")
def dashboard(username):
    user = fetchUser(username)
    username = user[1]
    posts = fetchPosts()

    profile = fetchProfile(user[2])
    return render_template("dashboard.html", username=user, posts=posts, fetchProfile=fetchProfile, fetchUser=fetchUser,
                           setLikes=setLikes)


@app.route("/login")
def loginPage():
    return render_template("login.html")


@app.route("/login_route",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        username = user[1]
        db_pass = user[3]
        cur.close()
        if user and db_pass == password:
            # return url_for('dashboard')
            session['email'] = email
            return redirect('/dashboard/' + email)
        else:
            return render_template('login.html');


@app.route("/signup")
def signupPage():
    return render_template("signup.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['confirm-password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone();
        if user:

            return render_template("userExist.html")
        else:
            if password == cpassword:
                cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                            (username, email, password))
                cur.execute(
                    "INSERT INTO profiles ( email,profileURL,role,year,semister,cgpa,about ) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (email, "", "", "", "", "", ""))
                cur.execute(
                    "INSERT INTO friends ( email,friend,requestes,no_of_friends ) VALUES (%s,%s,%s,%s)",
                    (email, "", "", "0"))


                mysql.connection.commit()

                mysql.connection.commit()
                cur.close();

                flash('User successfully registered!', 'success')
                return redirect('/login')
            else:
                return redirect('/signup')


@app.route('/dashboard/profile/<username>')
def profile(username):
    user = fetchUser(username)
    profile = fetchProfile(username)
    print(profile)
    return render_template('profile.html', username=user, profile=profile)


@app.route("/profile", methods=['GET', 'POST'])
def profileUpdate():
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        year = request.form['year']
        semister = request.form['semister']
        cgpa = request.form['cgpa']
        about = request.form['about']
        files = request.files.getlist('files[]')
        print(files)
        for file in files:
            # if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_query = "UPDATE profiles set profileURL=%s WHERE email=%s"
            cur = mysql.connection.cursor()

            cur.execute(update_query, (filename, email))
            print(file)
        cur = mysql.connection.cursor()

        update_query = "UPDATE profiles set role=%s , year = %s , semister = %s, cgpa=%s, about=%s WHERE email=%s"
        cur.execute(update_query, (role, year, semister, cgpa, about, email))
        mysql.connection.commit()

        cur.close()
        return redirect(url_for('profile', username=email))


@app.route("/dashboard/upload/<username>")
def upload(username):
    user = fetchUser(username)
    print(user)
    return render_template('upload.html', username=username)


@app.route("/upload", methods=['GET', 'POST'])
def uploadPost():
    if request.method == 'POST':
        postheader = request.form['postheader']
        description = request.form['description']
        files = request.files.getlist('files[]')
        now = datetime.now()
        username = session['email']
        user = fetchUser(username)
        print(user)
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(file)
        cur = mysql.connection.cursor()
        update_query = "UPDATE users set no_of_posts=no_of_posts+1 where email=%s"
        cur.execute(update_query, (username,))
        updated_user = fetchUser(username)
        print(username, username + str(updated_user[4]), filename, postheader, description, 0, 0, now)
        cur.execute(
            "INSERT INTO posts (postedby, postid, posturl,postheader,description,likes,comments,time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (username, username + str(updated_user[4]), filename, postheader, description, 0, 0, now))
        mysql.connection.commit()

    return redirect(url_for('dashboard', username=username))


@app.route("/dashboard/comments/<username>/<postid>")
def comments(username, postid):
    user = fetchUser(username)
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM comments WHERE postid=%s",)
    # comments =  fetchComments(postid)
    # print(comments)
    return render_template('comments.html', username=username, user=user, fetchComments=fetchComments, postid=postid,
                           fetchProfile=fetchProfile, fetchUser=fetchUser)


@app.route("/comment", methods=['GET', 'POST'])
def commentUpdate():
    if request.method == 'POST':
        comment = request.form['comment']
        postid = request.form['postid']
        now = datetime.now()
        username = session['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO comments (postid, commentby, comment,time) VALUES (%s, %s, %s,%s)",
                    (postid, username, comment, now))
        mysql.connection.commit()

    return redirect(url_for('dashboard', username=username))


@app.route("/posts/<username>")
def posts(username):
    # return "<h1>posts of %s" %username
    profile = fetchProfile(username)
    user = fetchUser(username)
    return render_template('posts.html', username=username, fetchUserPosts=fetchUserPosts, profile=profile, user=user)


@app.route("/dashboard/network/<username>")
def network(username):
    return render_template('network.html', username=username,fetchUser=fetchUser, fetchAllUser=fetchAllUser, fetchProfile=fetchProfile , fetchFriends=fetchFriends,fetchReq=fetchReq    )
    # return "<h1>network of %s</h1>" %username


@app.route("/network", methods=['GET', 'POST'])
def netwokUpdate():
    if request.method == 'POST':
        sender = request.form['sender']
        receiver = request.form['receiver']
        cur = mysql.connection.cursor()
        cur.execute("SELECT requestes FROM friends WHERE email=%s", (receiver,))
        req = cur.fetchone()
        # print(req[0])
        up = req[0].split(',')
        up.append(sender)
        # print(str(up))
        upres = ','.join(up)
        # print(upres)
        # print(up)

        print(type(req))
        cur.execute("INSERT INTO network (sender, reciver) VALUES (%s, %s)", (sender, receiver))
        update_query = "UPDATE friends set requestes=%s  where email=%s"
        cur.execute(update_query, (upres, receiver))

        mysql.connection.commit()

        print(sender, receiver)
        
        return redirect(url_for('network', username=sender))
    


@app.route("/dashboard/requests/<username>")
def requests(username):
    return render_template('request.html', username=username, fetchUser=fetchUser, fetchProfile=fetchProfile, fetchReq=fetchReq)


@app.route("/requestofuser" , methods=['GET', 'POST'] )
def requestsUpdate():
    if request.method == 'POST':
        user = request.form['user']
        receiver = request.form['receiver']
        print(user,receiver)
        cur = mysql.connection.cursor()
        cur.execute("SELECT requestes FROM friends WHERE email=%s", (user,))
        req = cur.fetchone()
        print('before:',req[0])
        up = req[0].split(',')
        print( up)
        up.remove(receiver)
        # print(str(up))
        upres = ','.join(up)
        print('updated:' ,upres)
        update_query = "UPDATE friends set requestes=%s  where email=%s"
        cur.execute(update_query, (upres, user))
        cur.execute("UPDATE friends set friend=%s  where email=%s", (receiver,user))
        cur.execute("UPDATE friends set friend=%s  where email=%s", (upres,receiver))
        cur.execute("UPDATE network set accept=%s  where reciver=%s", (True, user))

        mysql.connection.commit()

        # print(up)


    return render_template('request.html', username=user, fetchUser=fetchUser, fetchProfile=fetchProfile, fetchReq=fetchReq)




@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
