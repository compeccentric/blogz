from flask import Flask, request, redirect, render_template, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash

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
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
        

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title="Blogz!", users=users)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash('Logged in', 'correct')
            return redirect('/newpost')
        elif not user:
            flash('User does not exist', 'error')
        else:
            flash('Password is incorrect', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username=="" or password=="" or verify=="":
            flash('One or more fields are invalid', 'error')
            return redirect('/signup')
        if username == existing_user:
            flash('That username already exists', 'error')
            return redirect('/signup')
        if password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/signup')
        if len(username) < 3 or len(username) > 20:
            flash('Username is invalid','error')
            return redirect('/signup')
        if len(password) < 3 or len(password) > 20:
            flash('Password is invalid','error')
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('You have been logged out', 'correct')
    return redirect('/blog')



@app.route('/blog', methods=['POST', 'GET'])
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Blog.query.order_by(Blog.time.desc()).paginate(page, 5, False)
    next_url = url_for('blog', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog', page=posts.prev_num) \
        if posts.has_prev else None
    user_post = request.args.get("user")
    blog_post = request.args.get("id")
    if user_post:
        page = request.args.get('page', 1, type=int)
        posts = Blog.query.filter_by(owner_id=user_post).paginate(page, 5, False)
        next_url = url_for('blog', page=posts.next_num) \
            if posts.has_next else None
        prev_url = url_for('blog', page=posts.prev_num) \
            if posts.has_prev else None
        return render_template('user.html',title="Blogz!", posts=posts.items, next_url=next_url, prev_url=prev_url)
    if blog_post:
        posts = Blog.query.get(blog_post)
        return render_template('post.html',title="Blogz!", posts=posts)
    return render_template('blog.html',title="Blogz!", posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/newpost', methods=['POST', 'GET'])
def post():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(blog_title, blog_body, owner)
        if blog_title == "" and blog_body == "":
            return render_template("newpost.html", title_error = 'Please fill in the title', 
            body_error = 'Please fill in the body')
        if blog_title == "":
            return render_template("newpost.html", title_error = 'Please fill in the title', body=blog_body)
        if blog_body == "":
            return render_template("newpost.html", body_error = 'Please fill in the body', title=blog_title)    
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_post.id)) 
    return render_template('newpost.html')




if __name__ == '__main__':
    app.run()