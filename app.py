from app import create_app
from config import get_settings

app = create_app()

if __name__ == '__main__':
    settings = get_settings()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
