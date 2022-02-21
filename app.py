import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required, UserMixin
from random import randint
from requests import get
from bs4 import BeautifulSoup

app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "Hello World"

db = SQLAlchemy(app)

login_manager = LoginManager(app)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    reference_url = db.Column(db.String)
    content_url = db.Column(db.String)
    content = db.Column(db.String)
    tags = db.Column(db.String)


class ChessGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String)
    game_id = db.Column(db.String)


@app.route("/", methods=["POST", "GET"])
def index():
    if current_user.is_authenticated:
        if flask.request.method == "POST":
            tags = ""
            all_content = flask.request.values["content"].split(" ")
            for tag in range(len(all_content)):
                if "#" in all_content[tag]:
                    tags += f"{all_content[tag]}&&"
            new_post = Post(author=current_user.id, reference_url=None, content=flask.request.values["content"],
                            tags=tags)
            db.session.add(new_post)
            db.session.commit()

        posts = Post.query.order_by(Post.id.desc()).all()
        post_data = []
        for i in posts:
            post_data.append({
                "content": i.content,
                "author": User.query.get(i.author).username,
                "tags": i.tags,
                "img": i.content_url if "#image" in i.tags.split("&&") else None,
                "video": i.content_url if "#video" in i.tags.split("&&") else None,
                "game_url": i.reference_url if "#game" in i.tags.split("&&") else None
            })
        return flask.render_template("home.html", posts=post_data)

    if flask.request.method == "POST":
        target_user = User.query.filter_by(username=flask.request.values["username"]).first()
        if target_user.password == flask.request.values["password"]:
            login_user(target_user)
            return flask.redirect("/")

    return flask.render_template("index.html")


@app.route("/sign-up", methods=["POST", "GET"])
def signup():
    if flask.request.method == "POST":
        new_user = User(username=flask.request.values["username"], password=flask.request.values["password"])
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return flask.redirect("/")

    return flask.render_template("signup.html")


@app.route("/newgame/<game>")
@login_required
def start_game(game):
    if game == "chess":
        new_chess_game = ChessGame(game_id=randint(999999, 9999999),
                                   position="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        db.session.add(new_chess_game)

        new_post = Post(author=current_user.id, reference_url=f"/social-chess/{new_chess_game.game_id}",
                        content=f"{current_user.username} satranç oynamak istiyor", tags="#game&&#image",
                        content_url="https://www.pngplay.com/wp-content/uploads/2/Chess-Transparent-Free-PNG.png"
                        )

        db.session.add(new_post)

        db.session.commit()

        return flask.redirect(f"/social-chess/{new_chess_game.game_id}")

    if game == "battleship":
        game_id = randint(9999, 999999)
        new_post = Post(author=current_user.id, reference_url=f"http:"
                                                              f"//en.battleship-game.org/id{game_id}",
                        content=f"{current_user.username} battleship oynamak istiyor", tags="#game&&#image",
                        content_url="https://www.19fortyfive.com/wp-content/uploads/2021/07"
                                    "/USS-New-Jersey.jpg-1-1024x576.jpg"
                        )

        db.session.add(new_post)

        db.session.commit()

        return flask.redirect(f"http://en.battleship-game.org/id{game_id}", code=302)

    if game == "rps":
        game_id = randint(9999, 999999)
        new_post = Post(author=current_user.id,
                        reference_url=f"https://www.rpsgame.org/room?id={game_id}",
                        content=f"{current_user.username} taş kağıt makas oynamak istiyor", tags="#game&&#image",
                        content_url="https://media.istockphoto.com/vectors/rock-paper-scissors-icons-vector-id839977330?k=20&m=839977330&s=170667a&w=0&h=nzi9QwP0RRTeVV1Nn9bf6i7bgPFCrr_dxpUGMZRmJB8="
                        )

        db.session.add(new_post)

        db.session.commit()

        return flask.redirect(f"https://www.rpsgame.org/room?id={game_id}", code=302)


@app.route("/social-chess/img/chesspieces/wikipedia/<image_path>")
def return_chess_piece(image_path):
    return flask.send_file(f"wikipedia/{image_path}")


@app.route("/social-chess/<chess_id>")
@login_required
def play_chess(chess_id):
    return flask.render_template("chess.html")
