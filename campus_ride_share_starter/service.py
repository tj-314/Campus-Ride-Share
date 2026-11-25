import sqlite3
from contextlib import contextmanager
from datetime import date
from models import RidePost

class PostService:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL, post_type TEXT NOT NULL, destination TEXT NOT NULL, travel_date TEXT NOT NULL, departure_time TEXT NOT NULL, contact TEXT NOT NULL, seats INTEGER)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        try:
            db.row_factory = sqlite3.Row
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def authorize_owner(actor, owner):
        if not actor:  # B1: no authenticated identity
            raise PermissionError("Sign in first.")
        if actor != owner:  # B2: another student's post
            raise PermissionError("Only the owner may change this post.")
        return True  # B3: owner authorized

    def create(self, actor, data):
        if not actor:
            raise PermissionError("Sign in first.")
        valid = RidePost.validate(data)
        with self.connect() as db:
            cur = db.execute("INSERT INTO posts (owner,post_type,destination,travel_date,departure_time,contact,seats) VALUES (?,?,?,?,?,?,?)", (actor, *[valid[k] for k in ("post_type","destination","travel_date","departure_time","contact","seats")]))
            return cur.lastrowid

    def get(self, actor, post_id):
        if not actor:
            raise PermissionError("Sign in first.")
        with self.connect() as db:
            row = db.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        if row is None:
            raise LookupError("Post not found.")
        return dict(row)

    def browse(self, actor, destination="", travel_date="", mine=False):
        if not actor:
            raise PermissionError("Sign in first.")
        with self.connect() as db:
            rows = db.execute("SELECT * FROM posts ORDER BY travel_date,departure_time,id").fetchall()
        return [dict(r) for r in rows if
                ((mine and r["owner"] == actor) or (not mine and r["travel_date"] >= date.today().isoformat()))
                and destination.casefold() in r["destination"].casefold()
                and (not travel_date or r["travel_date"] == travel_date)]

    def update(self, actor, post_id, data):
        post = self.get(actor, post_id)
        self.authorize_owner(actor, post["owner"])
        valid = RidePost.validate(data)
        if valid["post_type"] != post["post_type"]:
            raise ValueError("Post type cannot be changed.")
        with self.connect() as db:
            db.execute("UPDATE posts SET destination=?,travel_date=?,departure_time=?,contact=?,seats=? WHERE id=?", (*[valid[k] for k in ("destination","travel_date","departure_time","contact","seats")], post_id))

    def delete(self, actor, post_id, confirmed=False):
        post = self.get(actor, post_id)
        self.authorize_owner(actor, post["owner"])
        if not confirmed:
            return False
        with self.connect() as db:
            db.execute("DELETE FROM posts WHERE id=?", (post_id,))
        return True
