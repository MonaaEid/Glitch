from fastapi import FastAPI, Request, Depends
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from typing import Optional
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from fastapi.templating import Jinja2Templates

from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
#  @app.middleware("http")
template = Jinja2Templates(directory="templates")
class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            return None

        username: Optional[str] = schemas.decode_access_token(token)
        if username:
            try:
                db: Session = next(get_db())
                user = schemas.get_user(db, username)
                if user:
                    return AuthCredentials(["authenticated"]), SimpleUser(username)
            except Exception as e:
                print(f"Error fetching user: {e}")
        return None

    


app = FastAPI(middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())])

@app.middleware("http")
async def add_middleware(request: Request, call_next):
    response = await call_next(request)
    return response

# @app.route("/")
# async def homepage(request: Request):
#     if request.user.is_authenticated:
#         return PlainTextResponse('Hello, ' + request.user.display_name)
#     return PlainTextResponse('Hello, you')

routes = [
    Route("/")
]
middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
]

app = FastAPI(routes=routes, middleware=middleware)
