from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator

from sqlalchemy import String, Integer, DateTime, Index, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, update, case, and_, func

from collections import defaultdict

from constants.services import Service, service_names_map


# --- SQLAlchemy Base ---
class Base(DeclarativeBase):
    pass


# --- Song Model ---
class Song(Base):
    __tablename__ = "songs"

    # Required fields
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    originalVersionId: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    defaultName: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    defaultNameLanguage: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    artistString: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lengthSeconds: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    pvServices: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    minMilliBpm: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    maxMilliBpm: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    songType: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    favoritedTimes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    ratingScore: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    createDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    publishDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    version: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # JSON fields
    additionalNames: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    pvs: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    views: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    artists: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)


class SongURL(Base):
    __tablename__ = "songurls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pv_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    service: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    views: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    dislikes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    favorites: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), 
        server_default=func.now(),
        onupdate=func.now()
    )


# --- Repository Class ---
class SongRepository:
    def __init__(self, db_url: str, echo: bool = False):
        self.engine = create_async_engine(db_url, echo=echo)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

        # Internal states for batching
        self._last_id = -1
        self._last_ids = defaultdict(lambda: -1)

    async def init_models(self):
        """Create tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def insert_songs(self, songs: List[dict]):
        async with self.session_factory() as session:
            song_objects = [Song(**song) for song in songs]
            session.add_all(song_objects)
            await session.commit()

    async def insert_song(self, song: dict):
        await self.insert_songs([song])

    async def fetch_unprocessed_songs_batch(self, batch_size: int = 1000) -> List[Song]:
        async with self.session_factory() as session:
            stmt = select(Song).order_by(Song.id).limit(batch_size)

            stmt = stmt.where(
                and_(
                    Song.views.is_(None),
                    func.jsonb_array_length(Song.pvs) > 0
                )
            )

            if (self._last_id is not None):
                stmt = stmt.where(Song.id > self._last_id)

            result = await session.execute(stmt)
            rows: List[Song] = result.scalars().all()

            if (rows):
                self._last_id = rows[-1].id

            return rows

    async def update_songs_batch(self, updates: list[dict]):
        if (not updates):
            return

        async with self.session_factory() as session:
            stmt = update(Song)

            await session.execute(stmt, updates)
            await session.commit()

    def reset_songs_batches(self):
        self._last_id = -1



    async def get_songurls_by_urls(self, urls: List[str]) -> List[SongURL]:
        if (not urls):
            return []

        async with self.session_factory() as session:
            stmt = select(SongURL).where(SongURL.url.in_(urls))
            result = await session.execute(stmt)
            return result.scalars().all()
        
    async def insert_song_urls(self, song_urls: List[dict]):
        async with self.session_factory() as session:
            song_objects = [SongURL(**song) for song in song_urls]
            session.add_all(song_objects)
            await session.commit()

    async def insert_song_url(self, song_url: dict):
        await self.insert_song_urls([song_url])

    async def _fetch_unprocessed_service_song_URLs_batch(self, service_name: str, batch_size: int = 50) -> List[SongURL]:
        async with self.session_factory() as session:
            stmt = select(SongURL).order_by(SongURL.id).limit(batch_size)

            stmt = stmt.where(
                and_(
                    SongURL.service == service_name,
                    SongURL.views.is_(None)
                )
            )

            if (self._last_id is not None):
                stmt = stmt.where(SongURL.id > 0)

            result = await session.execute(stmt)
            rows: List[SongURL] = result.scalars().all()

            if (rows):
                self._last_ids[service_name] = rows[-1].id

            return rows
        
    def _reset_service_song_URLs_batches(self, service_name: str):
        self._last_ids[service_name] = -1



    async def fetch_unprocessed_yt_batch(self, batch_size: int = 50) -> List[SongURL]:
        return await self._fetch_unprocessed_service_song_URLs_batch(
            service_names_map[Service.YOUTUBE], 
            batch_size
        )
    
    async def fetch_unprocessed_nn_batch(self, batch_size: int = 50) -> List[SongURL]:
        return await self._fetch_unprocessed_service_song_URLs_batch(
            service_names_map[Service.NICONICO], 
            batch_size
        )
    
    async def fetch_unprocessed_bb_batch(self, batch_size: int = 50) -> List[SongURL]:
        return await self._fetch_unprocessed_service_song_URLs_batch(
            service_names_map[Service.BILIBILI], 
            batch_size
        )

    async def update_song_urls_batch(self, updates: list[dict]):
        if (not updates):
            return

        async with self.session_factory() as session:
            stmt = update(SongURL)

            await session.execute(stmt, updates)
            await session.commit()

    def reset_yt_batches(self):
        self._reset_service_song_URLs_batches(
            service_names_map[Service.YOUTUBE]
        )

    def reset_nn_batches(self):
        self._reset_service_song_URLs_batches(
            service_names_map[Service.NICONICO]
        )

    def reset_bb_batches(self):
        self._reset_service_song_URLs_batches(
            service_names_map[Service.BILIBILI]
        )



    async def fetch_joined_views_in_batches(
        self, batch_size: int = 1000
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        last_id = -1
        while True:
            async with self.session_factory() as session:
                # fetch batch of songs
                songs = (
                    await session.execute(
                        select(Song.id, Song.pvs)
                        .where(Song.id > last_id)
                        .order_by(Song.id)
                        .limit(batch_size)
                    )
                ).all()

                if (not songs):
                    break

                song_ids = [s.id for s in songs]

                # fetch related SongURLs
                songurls = (
                    await session.execute(
                        select(SongURL.song_id, SongURL.url, SongURL.views, SongURL.service)
                        .where(SongURL.song_id.in_(song_ids))
                    )
                ).all()

                # group by song_id and url
                urls_by_song: Dict[int, Dict[str, Dict[str, Any]]] = {}
                for su in songurls:
                    urls_by_song.setdefault(su.song_id, {})[su.url] = {
                        "views": su.views,
                        "service": su.service,
                    }

                batch_result = []
                for s in songs:
                    services: Dict[str, List[Dict[str, Any]]] = {}

                    for pv_url in (s.pvs or []):  # preserve pvs order
                        url_info = urls_by_song.get(s.id, {}).get(pv_url["url"])
                        if url_info:
                            services.setdefault(url_info["service"], []).append({
                                "url": pv_url["url"],
                                "views": url_info["views"]
                            })

                    batch_result.append({
                        "song_id": s.id,
                        "services": services
                    })

                yield batch_result

                last_id = song_ids[-1]
