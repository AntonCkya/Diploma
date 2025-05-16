from sqlalchemy import Boolean, Column, Integer, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "music_users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True)
    username = Column(String, unique=True, index=True)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True)
    username = Column(String, unique=True, index=True)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    duration = Column(Integer)
    file_url = Column(String)
    artist_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    title = Column(String)
    cover_image_url = Column(String)
    release_date = Column(DateTime, default=datetime.utcnow)
    type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlbumTrack(Base):
    __tablename__ = "albums_tracks"

    album_id = Column(Integer)
    track_id = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('album_id', 'track_id', name='albums_tracks_pkey'),
    )

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    track_id = Column(Integer)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Like(Base):
    __tablename__ = "likes"

    user_id = Column(Integer)
    track_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'track_id', name='likes_pkey'),
    )

class Subscribe(Base):
    __tablename__ = "subscriptions"

    user_id = Column(Integer)
    artist_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'artist_id', name='subscriptions_pkey'),
    )
