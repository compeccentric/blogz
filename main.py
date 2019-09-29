from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_post = request.args.get("id")
    if blog_post == None:
        posts = Blog.query.order_by(Blog.time.desc()).all()
        return render_template('blog.html',title="Build A Blog!", posts=posts)
    else:
        posts = Blog.query.get(blog_post)
        return render_template('post.html',title="Build A Blog!", posts=posts)



@app.route('/newpost', methods=['POST', 'GET'])
def post():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body)
        if blog_title == "" and blog_body == "":
            return render_template("newpost.html", title_error = 'Please fill in the title', 
            body_error = 'Please fill in the body')
        if blog_title == "":
            return render_template("newpost.html", title_error = 'Please fill in the title', body=blog_body)
        if blog_body == "":
            return render_template("newpost.html", body_error = 'Please fill in the body', title=blog_title)    
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog')
    return render_template('newpost.html')




if __name__ == '__main__':
    app.run()