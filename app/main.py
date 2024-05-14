from app import create_app

print("Running main.py")
app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['FLASK_DEBUG'])
