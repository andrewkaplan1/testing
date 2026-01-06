import sqlite3
import os
from datetime import datetime
from config import Config
import json

# Try to import psycopg2 for PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

class Database:
    def __init__(self, db_path=None):
        # Check if we should use PostgreSQL or SQLite
        self.database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
        self.use_postgres = bool(self.database_url and POSTGRES_AVAILABLE)
        self.db_path = db_path or Config.DATABASE_PATH

        if self.use_postgres:
            print("Using PostgreSQL database")
        else:
            print("Using SQLite database")

        self.init_db()

    def get_connection(self):
        if self.use_postgres:
            conn = psycopg2.connect(self.database_url)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def _get_cursor(self, conn):
        """Get a cursor with appropriate configuration for the database type"""
        if self.use_postgres:
            return conn.cursor(cursor_factory=RealDictCursor)
        else:
            return conn.cursor()

    def _placeholder(self):
        """Return the correct parameter placeholder for the database type"""
        return '%s' if self.use_postgres else '?'

    def init_db(self):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)

        if self.use_postgres:
            # PostgreSQL syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    author TEXT,
                    source TEXT,
                    content TEXT,
                    summary TEXT,
                    key_insights TEXT,
                    implications TEXT,
                    audio_path TEXT,
                    status TEXT DEFAULT 'unread',
                    favorited BOOLEAN DEFAULT FALSE,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    archived_at TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS digests (
                    id SERIAL PRIMARY KEY,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    article_ids TEXT,
                    cross_article_insights TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
        else:
            # SQLite syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    author TEXT,
                    source TEXT,
                    content TEXT,
                    summary TEXT,
                    key_insights TEXT,
                    implications TEXT,
                    audio_path TEXT,
                    status TEXT DEFAULT 'unread',
                    favorited BOOLEAN DEFAULT 0,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    archived_at TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS digests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    article_ids TEXT,
                    cross_article_insights TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

        conn.commit()
        conn.close()

    def add_article(self, url, title=None, author=None, source=None, content=None, tags=None):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)
        ph = self._placeholder()

        try:
            cursor.execute(f'''
                INSERT INTO articles (url, title, author, source, content, tags)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            ''', (url, title, author, source, content, json.dumps(tags) if tags else None))

            if self.use_postgres:
                cursor.execute('SELECT lastval()')
                article_id = cursor.fetchone()['lastval']
            else:
                article_id = cursor.lastrowid

            conn.commit()
            return article_id
        except (sqlite3.IntegrityError if not self.use_postgres else Exception) as e:
            # Article already exists
            conn.rollback()
            cursor.execute(f'SELECT id FROM articles WHERE url = {ph}', (url,))
            result = cursor.fetchone()
            return result['id'] if self.use_postgres else result[0]
        finally:
            conn.close()

    def update_article(self, article_id, **kwargs):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)
        ph = self._placeholder()

        # Build dynamic update query
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = {ph}")
            if isinstance(value, (list, dict)):
                values.append(json.dumps(value))
            else:
                values.append(value)

        values.append(article_id)

        query = f"UPDATE articles SET {', '.join(fields)} WHERE id = {ph}"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def get_article(self, article_id):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)
        ph = self._placeholder()
        cursor.execute(f'SELECT * FROM articles WHERE id = {ph}', (article_id,))
        article = cursor.fetchone()
        conn.close()
        return dict(article) if article else None

    def get_articles(self, status=None, limit=None, favorited=None):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)
        ph = self._placeholder()

        query = 'SELECT * FROM articles WHERE 1=1'
        params = []

        if status:
            query += f' AND status = {ph}'
            params.append(status)

        if favorited is not None:
            query += f' AND favorited = {ph}'
            params.append(True if favorited else False)

        query += ' ORDER BY created_at DESC'

        if limit:
            query += f' LIMIT {ph}'
            params.append(limit)

        cursor.execute(query, params)
        articles = cursor.fetchall()
        conn.close()

        return [dict(article) for article in articles]

    def mark_as_read(self, article_id):
        self.update_article(article_id, status='read', read_at=datetime.now().isoformat())

    def mark_as_unread(self, article_id):
        self.update_article(article_id, status='unread', read_at=None)

    def archive_article(self, article_id):
        self.update_article(article_id, status='archived', archived_at=datetime.now().isoformat())

    def toggle_favorite(self, article_id):
        article = self.get_article(article_id)
        if article:
            new_favorited = 0 if article['favorited'] else 1
            self.update_article(article_id, favorited=new_favorited)
            return new_favorited
        return None

    def add_digest(self, article_ids, cross_article_insights):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)
        ph = self._placeholder()

        cursor.execute(f'''
            INSERT INTO digests (article_ids, cross_article_insights)
            VALUES ({ph}, {ph})
        ''', (json.dumps(article_ids), cross_article_insights))

        if self.use_postgres:
            cursor.execute('SELECT lastval()')
            digest_id = cursor.fetchone()['lastval']
        else:
            digest_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return digest_id

    def get_unread_articles_for_digest(self, hours=24):
        conn = self.get_connection()
        cursor = self._get_cursor(conn)
        ph = self._placeholder()

        if self.use_postgres:
            # PostgreSQL syntax for date comparison
            cursor.execute(f'''
                SELECT * FROM articles
                WHERE status = 'unread'
                AND created_at > NOW() - INTERVAL '1 hour' * {ph}
                ORDER BY created_at DESC
            ''', (hours,))
        else:
            # SQLite syntax
            cursor.execute(f'''
                SELECT * FROM articles
                WHERE status = 'unread'
                AND datetime(created_at) > datetime('now', '-' || {ph} || ' hours')
                ORDER BY created_at DESC
            ''', (hours,))

        articles = cursor.fetchall()
        conn.close()

        return [dict(article) for article in articles]
