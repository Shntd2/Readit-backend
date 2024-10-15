import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from flask_migrate import Migrate
from app_package import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)
