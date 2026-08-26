"""
services/database.py

SQLAlchemy + SQLite persistence layer, used for the app's "offline
mode" — a visitor can download a Tour once (while on the museum wifi)
and then follow it with no internet connection, since everything is
read from the local SQLite file afterwards.

These SQLAlchemy model classes are intentionally kept separate from
the pure-Python domain classes in models/. That separation is a
common real-world pattern: the domain classes (models/tour.py,
models/content.py) hold business logic and are what the rest of the
app works with; these ORM classes only exist to get that data in and
out of the database.
"""

import json
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from models.tour import Tour, TourStop
from models.content import AudioGuide, VideoGuide, TextGuide, ImageGuide, ModelGuide
from models.media import StopMedia
from models.social import Comment

Base = declarative_base()


class TourRecord(Base):
    """Database row representing a downloaded Tour."""

    __tablename__ = "tours"

    tour_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    theme = Column(String, nullable=False)
    language = Column(String, nullable=False, default="en")

    stops = relationship(
        "TourStopRecord", back_populates="tour", cascade="all, delete-orphan"
    )


class TourStopRecord(Base):
    """Database row representing one stop within a downloaded Tour."""

    __tablename__ = "tour_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tour_id = Column(String, ForeignKey("tours.tour_id"), nullable=False)
    name = Column(String, nullable=False)
    location_id = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    content_type = Column(String, nullable=False)  # "audio" | "video" | "text"
    content_title = Column(String, nullable=False)
    content_duration_seconds = Column(Integer, default=0)
    content_extra = Column(String, default="")  # narrator / resolution / body

    description = Column(String, default="")
    description_extra = Column(String, default="")  # JSON: translations
    media_extra = Column(String, default="")  # JSON: images/video_path/audio_path

    tour = relationship("TourRecord", back_populates="stops")


class CommentRecord(Base):
    """Database row for a comment a visitor left on a tour stop.

    Kept in its own table (rather than on TourStopRecord) since a stop
    can accumulate many comments from many visitors over time — this
    is what makes comments survive an app restart instead of living
    only in the in-memory Visitor object for that one session.
    """

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tour_id = Column(String, nullable=False)
    visitor_id = Column(String, nullable=False)
    location_id = Column(String, nullable=False)
    text = Column(String, nullable=False)
    posted_at = Column(DateTime, default=datetime.utcnow)


def _load_extra(raw: str) -> dict:
    """
    Parses the JSON-encoded content_extra column back into a dict.
    Falls back to an empty dict for old/unrecognized data rather than
    crashing, so a tour saved before this format existed can still be
    reloaded (just without its type-specific extras).
    """
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


class OfflineTourStore:
    """
    Facade over the SQLAlchemy session that the rest of the app uses.
    Hides all ORM/session details behind three simple methods:
    save_tour, load_tour, list_downloaded_tours.
    """

    def __init__(self, db_path: str = "museum_tours.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self._migrate_schema()
        self.Session = sessionmaker(bind=self.engine)

    def _migrate_schema(self) -> None:
        """Add any columns a current TourStopRecord defines that an
        existing (older) database file on disk doesn't have yet.

        Base.metadata.create_all() above only creates tables that are
        missing entirely — it never alters a table that already
        exists on disk. So a museum_tours.db left over from an older
        version of this app (before the description/media columns
        were added) would otherwise make every save fail with a
        "no such column" error. This brings an old file up to date
        automatically instead of requiring anyone to delete it.
        """
        with self.engine.connect() as conn:
            existing_columns = {
                row[1] for row in conn.exec_driver_sql("PRAGMA table_info(tour_stops)")
            }
            for column in TourStopRecord.__table__.columns:
                if column.name in existing_columns:
                    continue
                col_type = "INTEGER" if isinstance(column.type, Integer) else "TEXT"
                conn.exec_driver_sql(
                    f"ALTER TABLE tour_stops ADD COLUMN {column.name} {col_type}"
                )
            conn.commit()

    def save_tour(self, tour: Tour) -> None:
        session = self.Session()
        try:
            session.merge(
                TourRecord(
                    tour_id=tour.tour_id,
                    title=tour.title,
                    theme=tour.theme,
                    language=tour.language,
                )
            )
            # Replace existing stops for this tour with the current set.
            session.query(TourStopRecord).filter_by(tour_id=tour.tour_id).delete()
            for stop in tour.stops:
                content = stop.content
                content_type, extra = self._describe_content(content)
                media = stop.media
                session.add(
                    TourStopRecord(
                        tour_id=tour.tour_id,
                        name=stop.name,
                        location_id=stop.location_id,
                        order=stop.order,
                        content_type=content_type,
                        content_title=content.title,
                        content_duration_seconds=content.duration_seconds,
                        content_extra=extra,
                        description=stop.description,
                        description_extra=json.dumps(stop._description_translations),
                        media_extra=json.dumps({
                            "images": media.images,
                            "video_path": media.video_path,
                            "audio_path": media.audio_path,
                            "audio_path_translations": media.audio_path_translations,
                        }),
                    )
                )
            session.commit()
        finally:
            session.close()

    def load_tour(self, tour_id: str) -> Tour:
        session = self.Session()
        try:
            record = session.get(TourRecord, tour_id)
            if record is None:
                raise KeyError(f"No offline tour with id {tour_id}")
            tour = Tour(record.tour_id, record.title, record.theme, record.language)
            for stop_record in sorted(record.stops, key=lambda s: s.order):
                content = self._rebuild_content(stop_record)
                media_extra = _load_extra(stop_record.media_extra)
                media = StopMedia(
                    images=media_extra.get("images", []),
                    video_path=media_extra.get("video_path"),
                    audio_path=media_extra.get("audio_path"),
                    audio_path_translations=media_extra.get("audio_path_translations", {}),
                )
                tour.add_stop(
                    TourStop(
                        name=stop_record.name,
                        location_id=stop_record.location_id,
                        content=content,
                        order=stop_record.order,
                        description=stop_record.description or "",
                        description_translations=_load_extra(stop_record.description_extra),
                        media=media,
                    )
                )
            return tour
        finally:
            session.close()

    def list_downloaded_tours(self):
        session = self.Session()
        try:
            return [r.tour_id for r in session.query(TourRecord).all()]
        finally:
            session.close()

    def save_comment(self, tour_id: str, comment: "Comment") -> None:
        """Persists a visitor's comment so it's still there the next
        time this tour is opened, on this device or another one
        sharing the same offline store — not just for the rest of the
        current in-memory session."""
        session = self.Session()
        try:
            session.add(
                CommentRecord(
                    tour_id=tour_id,
                    visitor_id=comment.visitor_id,
                    location_id=comment.location_id,
                    text=comment.text,
                    posted_at=comment.posted_at,
                )
            )
            session.commit()
        finally:
            session.close()

    def list_comments(self, tour_id: str) -> list:
        """Returns every saved Comment for a tour, oldest first."""
        session = self.Session()
        try:
            records = (
                session.query(CommentRecord)
                .filter_by(tour_id=tour_id)
                .order_by(CommentRecord.posted_at)
                .all()
            )
            return [
                Comment(r.visitor_id, r.location_id, r.text, posted_at=r.posted_at)
                for r in records
            ]
        finally:
            session.close()

    @staticmethod
    def _describe_content(content):
        translations = getattr(content, "_translations", None) or None
        if isinstance(content, AudioGuide):
            return "audio", json.dumps({
                "narrator": content.narrator, "script": content.script,
                "audio_path": content.audio_path, "translations": translations,
            })
        if isinstance(content, VideoGuide):
            return "video", json.dumps({
                "resolution": content.resolution, "frames_dir": content.frames_dir,
                "frame_count": content.frame_count, "caption": content.caption,
                "translations": translations,
            })
        if isinstance(content, ImageGuide):
            return "image", json.dumps({
                "image_path": content.image_path, "caption": content.caption,
                "translations": translations,
            })
        if isinstance(content, ModelGuide):
            return "model", json.dumps({
                "model_path": content.model_path, "format": content.format,
                "shape": content.shape, "translations": translations,
            })
        if isinstance(content, TextGuide):
            return "text", json.dumps({"body": content.body, "translations": translations})
        return "text", json.dumps({"body": ""})

    @staticmethod
    def _rebuild_content(stop_record: TourStopRecord):
        extra = _load_extra(stop_record.content_extra)
        title = stop_record.content_title
        duration = stop_record.content_duration_seconds
        translations = extra.get("translations")

        if stop_record.content_type == "audio":
            return AudioGuide(
                title, duration,
                narrator=extra.get("narrator", "Museum Staff"),
                script=extra.get("script", ""),
                audio_path=extra.get("audio_path"),
                translations=translations,
            )
        if stop_record.content_type == "video":
            return VideoGuide(
                title, duration,
                resolution=extra.get("resolution", "1080p"),
                frames_dir=extra.get("frames_dir"),
                frame_count=extra.get("frame_count", 0),
                caption=extra.get("caption", ""),
                translations=translations,
            )
        if stop_record.content_type == "image":
            return ImageGuide(
                title, image_path=extra.get("image_path", ""),
                caption=extra.get("caption", ""),
                duration_seconds=duration, translations=translations,
            )
        if stop_record.content_type == "model":
            return ModelGuide(
                title, model_path=extra.get("model_path", ""),
                format=extra.get("format", "glb"), duration_seconds=duration,
                shape=extra.get("shape", "vase"), translations=translations,
            )
        return TextGuide(title, body=extra.get("body", ""), translations=translations)
