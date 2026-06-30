from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.secret_key = "instagram_clone"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# USERS
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))

    bio = db.Column(db.String(200), default="")

    followers = db.Column(db.Integer, default=0)

    following = db.Column(db.Integer, default=0)

# POSTS
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video = db.Column(db.String(200))
    song = db.Column(db.String(200))
    user = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    user = db.Column(db.String(100))
    text = db.Column(db.String(300))


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# HOME (FEED)
@app.route("/")
@login_required
def home():

    posts = Post.query.order_by(Post.id.desc()).all()
    comments = Comment.query.all()

    return render_template("index.html", posts=posts, comments=comments)

# UPLOAD POST
@app.route("/upload", methods=["POST"])
@login_required
def upload():

    video = request.files["video"]
    song = request.form["song"]

    path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
    video.save(path)

    post = Post(
        video=video.filename,
        song=song,
        user=current_user.username,
        likes=0
    )

    db.session.add(post)
    db.session.commit()

    return redirect("/")


# LIKE (toggle style)
@app.route("/like/<int:id>")
@login_required
def like(id):

    post = Post.query.get(id)

    post.likes += 1
    db.session.commit()

    return redirect("/")

@app.route("/profile/<username>")
@login_required
def profile(username):

    user = User.query.filter_by(username=username).first()

    posts = Post.query.filter_by(user=username).all()

    return render_template(
        "profile.html",
        user=user,
        posts=posts
    )
# CHANGE SONG
@app.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment(post_id):

    text = request.form["text"]

    new_comment = Comment(
        post_id=post_id,
        user=current_user.username,
        text=text
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect("/")

# AUTH (simple)
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        user = User(username=request.form["username"], password=request.form["password"])
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            login_user(user)
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)