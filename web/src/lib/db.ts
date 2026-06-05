import Database from 'better-sqlite3';
import path from 'path';

// Path to the original library.db file in the Python project root
// Assuming Next.js app is at /Users/hibadhaoui/Desktop/bibliotheque_ia/web
const dbPath = path.join(process.cwd(), '..', 'library.db');

export function getDb() {
  const db = new Database(dbPath, {
    // You can add verbose: console.log if you need to debug SQL queries
  });
  
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
        password_hash     TEXT    NOT NULL
    );
  `);
  
  return db;
}
