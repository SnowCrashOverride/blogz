from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
   

    def __init__(self, title, body):
        self.title = title
        self.body = body
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'newpost', 'singleUser', 'entry', 'base']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')   

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            return redirect('/')
        else:
            # TODO - explain why login failed
            return '<h1>Error!</h1>'

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    id = request.args.get('id')

    if not id:
        return render_template('blog.html', blogs=blogs)

    else: 
        blog = Blog.query.get(id)
        title = blog.title
        body = blog.body
        return render_template('entry.html', blog_title=title, blog_body=body)




@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = "Please give your blog a title"
    body_error = "Please write some stuff"


    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        
        if (not blog_title) or (blog_title.strip() == ""):
            if (not blog_body) or (blog_body.strip() == ""):
                return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)  
            else:
                return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error)

        if (not blog_body) or (blog_body.strip() == ""):
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, body_error=body_error)

        if (not blog_title) or (blog_title.strip() == "") and (not blog_body) or (blog_body.strip() == ""): 
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)  
        
        else: 
            new_post = Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()
            just_posted = db.session.query(Blog).order_by(Blog.id.desc()).first()
            id = str(just_posted.id)
            return redirect('/blog?id=' + id)




@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('blog.html')


if __name__ == '__main__':
    app.run()