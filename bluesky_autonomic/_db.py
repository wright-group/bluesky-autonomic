__all__ = ["connection"]

import pathlib
import appdirs
import sqlite3


path = pathlib.Path(appdirs.user_data_dir("bluesky_autonomic", "bluesky_autonomic")) / "state.db"

path.parent.mkdir(parents=True, exist_ok=True)

connection = sqlite3.connect(path)
cur = connection.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS enable (opa VARCHAR NOT NULL, delay VARCHAR NOT NULL, enable INTEGER DEFAULT 0, PRIMARY KEY(opa, delay))")
cur.execute("CREATE TABLE IF NOT EXISTS delay (delay VARCHAR NOT NULL PRIMARY KEY, zero_position REAL NOT NULL)")
