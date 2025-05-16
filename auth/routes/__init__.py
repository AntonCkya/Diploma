from routes.register import api_router as register_api_router
from routes.login import api_router as login_api_router
from routes.logout import api_router as logout_api_router
from routes.me import api_router as me_api_router

list_of_routes = [
    register_api_router,
    login_api_router,
    logout_api_router,
    me_api_router,
]

__all__ = [
    "list_of_routes",
]