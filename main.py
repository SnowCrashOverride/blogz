from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://goodmusics:goodmusics@localhost:8889/goodmusics'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'thx1138'


class Music(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    artist = db.Column(db.String(120))
    cover = db.Column(db.String(500))
    rating = db.Column(db.String(120))
    date = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   

    def __init__(self, title, artist, cover, rating, date, owner):
        self.title = title
        self.artist = artist
        self.cover = cover
        self.rating = rating
        self.date = date
        self.owner = owner
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    musics = db.relationship('Music', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password





@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'music', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password != password:
            session['username'] = username
            flash("This isn't the correct password")
            return render_template('login.html', username=username)
        if user and user.password == password:
            session['username'] = username
            flash("Log in successful!")
            return redirect('/newpost')
        else:
            flash("Username does not exist")
            return render_template('login.html')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = "Please enter a valid username"
    username_error2 = "That username has already been taken"
    password_error = "Please enter a valid password"
    verify_error = "Please verify your password"
    

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('signup.html', username_error2=username_error2)
            
        else:

            if (not username) or (username.strip() == "") or len(username) < 3 or len(username) > 20 or (" " in username.strip()):
                if (not password) or (password.strip() == "") or len(password) < 3 or len(password) > 20 or (" " in password.strip()):
                    if not verify or (verify.strip() == "") or (verify != password):
                        return render_template('signup.html', username=username, 
                        username_error=username_error, password_error=password_error, verify_error=verify_error)  
                    else:
                        return render_template('signup.html', username=username,
                        username_error=username_error, password_error=password_error)
                else:
                    return render_template('signup.html', username=username,
                    username_error=username_error)

            if (not password) or (password.strip() == "") or len(password) < 3 or len(password) > 20 or (" " in password.strip()):
                if (not verify) or (verify.strip() == "") or (verify != password):
                    return render_template('signup.html', username=username,  
                    password_error=password_error, verify_error=verify_error)  
                else:
                    return render_template('signup.html', username=username, 
                    password_error=password_error)
        
            if (not verify) or (verify.strip() == "") or (verify != password):
                return render_template('signup.html', username=username,
                verify_error=verify_error)  
                
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            


@app.route('/music', methods=['POST', 'GET'])
def music():
    
    user = request.args.get('user')
    id = request.args.get('id')
    
    if user:
        musics_by = Music.query.filter_by(owner_id=user).all()
        return render_template('singleUser.html', musics_by=musics_by)

    if id:
        musics = Music.query.filter_by(id=id).all()
        return render_template('music.html', musics=musics)
    
    else:
        musics = Music.query.all()
        return render_template('music.html', musics=musics)


    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = "Title it!"
    artist_error = "Who is the artist?"
    cover_error = "Add a cover!"
    #rating_error = "Rate it!"
    date_error = "Add the date"


    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        music_title = request.form['title']
        music_artist = request.form['artist']
        music_cover = request.form['cover']
        music_rating = request.form['rating']
        music_date = request.form['date']

        
        if (not music_title) or (music_title.strip() == ""):
            if (not music_cover) or (music_cover.strip() == ""):
                return render_template('newpost.html', music_title=music_title, music_cover=music_cover, title_error=title_error, cover_error=cover_error)  
            else:
                return render_template('newpost.html', music_title=music_title, music_cover=music_cover, title_error=title_error)

        if (not music_cover) or (music_cover.strip() == ""):
            return render_template('newpost.html', music_title=music_title, music_cover=music_cover, cover_error=cover_error)

        if (not music_title) or (music_title.strip() == "") and (not music_cover) or (music_cover.strip() == ""): 
            return render_template('newpost.html', music_title=music_title, music_cover=music_cover, title_error=title_error, cover_error=cover_error)  
        
        else: 
            music_owner = User.query.filter_by(username=session['username']).first()
            new_post = Music(music_title, music_artist, music_cover, music_rating, music_date, music_owner) # user.id
            db.session.add(new_post)
            db.session.commit()
            just_posted = db.session.query(Music).order_by(Music.id.desc()).first()
            id = str(just_posted.id)
            return redirect('/music?id=' + id)



@app.route('/logout')
def logout():
    del session['username']
    return redirect('/music')
    


@app.route('/', methods=['POST', 'GET'])
def index():
    allusers = User.query.all()
    return render_template('index.html', users=allusers)


if __name__ == '__main__':
    app.run()