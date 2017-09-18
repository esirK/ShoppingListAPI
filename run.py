import os

from app import create_app

app = create_app(os.environ.get('CURRENT_CONFIG'))

if __name__ == '__main__':
    app.run(debug=True)
