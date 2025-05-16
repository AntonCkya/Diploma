from routes.users import api_router as users_api_router
from routes.tracks import api_router as tracks_api_router 
from routes.albums import api_router as albums_api_router 
from routes.comments import api_router as comments_api_router 
from routes.likes import api_router as likes_api_router 
from routes.subs import api_router as subs_api_router 

list_of_routes = [
    users_api_router,
    tracks_api_router,
    albums_api_router,
    comments_api_router,
    likes_api_router,
    subs_api_router,
]

__all__ = [
    "list_of_routes",
]
