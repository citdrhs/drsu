from flask import Flask, render_template
from .forms import RegisterForm, LoginForm

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@https://domain:port/databasename'

    @app.route("/")
    def index():
        return render_template("home.html")
    
    @app.route("/login")
    def login():
        loginform = LoginForm
        return render_template("login.html", form = loginform)
    
    @app.route("/register")
    def register():
        registerform = RegisterForm
        return render_template("register.html", form = registerform)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)

