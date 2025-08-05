import uvicorn
from app.utils.enviroment import settings


def start_server():
    port = int(settings.port)
    uvicorn.run("app:create_app", host="0.0.0.0",
                port=port, reload=True, factory=True)


if __name__ == "__main__":
    start_server()
