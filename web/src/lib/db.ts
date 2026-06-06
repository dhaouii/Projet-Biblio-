import Database from 'better-sqlite3';
import path from 'path';

// Path to the original library.db file in the Python project root
// Assuming Next.js app is at /Users/hibadhaoui/Desktop/bibliotheque_ia/web
const dbPath = path.join(process.cwd(), '..', 'library.db');

// SHA-256 hashes for the demo accounts (matches the Python hashlib.sha256 scheme)
// admin / admin  and  user / user
const DEMO_ADMIN_HASH = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918';
const DEMO_USER_HASH = '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb';

export function getDb() {
  const db = new Database(dbPath);

  // Create tables if they don't exist (mirroring the python db_manager logic)
  db.exec(`
    CREATE TABLE IF NOT EXISTS livres (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        titre             TEXT    NOT NULL,
        auteur            TEXT    NOT NULL,
        categorie         TEXT    NOT NULL,
        annee_publication INTEGER NOT NULL,
        quantite          INTEGER DEFAULT 1,
        statut            TEXT    DEFAULT 'disponible'
    );

    CREATE TABLE IF NOT EXISTS utilisateurs (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        username          TEXT    NOT NULL UNIQUE,
        password_hash     TEXT    NOT NULL,
        role              TEXT    NOT NULL DEFAULT 'user',
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS api_keys (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        key_type          TEXT    NOT NULL,
        key_value         TEXT    NOT NULL,
        is_active         BOOLEAN DEFAULT 1,
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  // For databases created by an older version (no `role` column), add it safely.
  try {
    db.exec(`ALTER TABLE utilisateurs ADD COLUMN role TEXT NOT NULL DEFAULT 'user'`);
  } catch {
    // Column already exists — ignore.
  }

  // Seed the two demo accounts the first time the users table is empty.
  const { count } = db.prepare('SELECT COUNT(*) AS count FROM utilisateurs').get() as { count: number };
  if (count === 0) {
    const insert = db.prepare(
      'INSERT INTO utilisateurs (username, password_hash, role) VALUES (?, ?, ?)'
    );
    insert.run('admin', DEMO_ADMIN_HASH, 'admin');
    insert.run('user', DEMO_USER_HASH, 'user');
  }

  return db;
}
