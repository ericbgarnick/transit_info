from flaskr import create_app, set_g


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        set_g()
