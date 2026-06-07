import sqlite3

DB_FILE = "server_vault.db"
SERVER_ACTIVE = True

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_vault (
        username TEXT PRIMARY KEY,
        server_share TEXT NOT NULL,
        vault_blob BLOB NOT NULL,
        nonce BLOB NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def save_vault(username, server_share, vault_blob, nonce):
    if not SERVER_ACTIVE:
        return None
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO user_vault (username, server_share, vault_blob, nonce)
    VALUES (?, ?, ?, ?)
    """, (username, server_share, vault_blob, nonce))
    conn.commit()
    conn.close()

def get_vault(username):
    if not SERVER_ACTIVE:
        return None
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    SELECT server_share, vault_blob, nonce
    FROM user_vault
    WHERE username = ?
    """, (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None

    return {
        "server_share": row[0],
        "vault_blob": row[1],
        "nonce": row[2]
    }