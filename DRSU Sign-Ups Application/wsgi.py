import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=int(os.environ.get('APP_PORT', 5433)))

