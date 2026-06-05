'use server';

import { getDb } from '@/lib/db';
import { revalidatePath } from 'next/cache';

export interface DbBook {
  id: number;
  titre: string;
  auteur: string;
  categorie: string;
  annee_publication: number;
  quantite: number;
  statut: 'disponible' | 'emprunté' | 'réservé';
}

export interface LibraryStats {
  total: number;
  disponibles: number;
  empruntes: number;
  reserves: number;
  categories: number;
}

export async function getBooks(): Promise<DbBook[]> {
  const db = getDb();
  const stmt = db.prepare('SELECT * FROM livres ORDER BY id DESC');
  return stmt.all() as DbBook[];
}

export async function searchBooks(query: string): Promise<DbBook[]> {
  const db = getDb();
  const term = `%${query.toLowerCase()}%`;
  const stmt = db.prepare(`
    SELECT * FROM livres
    WHERE LOWER(titre) LIKE ?
       OR LOWER(auteur) LIKE ?
       OR LOWER(categorie) LIKE ?
    ORDER BY titre
  `);
  return stmt.all(term, term, term) as DbBook[];
}

export async function getStats(): Promise<LibraryStats> {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN statut = 'disponible' THEN 1 ELSE 0 END) as disponibles,
      SUM(CASE WHEN statut = 'emprunté'   THEN 1 ELSE 0 END) as empruntes,
      SUM(CASE WHEN statut = 'réservé'    THEN 1 ELSE 0 END) as reserves,
      COUNT(DISTINCT categorie) as categories
    FROM livres
  `);
  const row = stmt.get() as any;
  return {
    total: row.total || 0,
    disponibles: row.disponibles || 0,
    empruntes: row.empruntes || 0,
    reserves: row.reserves || 0,
    categories: row.categories || 0,
  };
}

export async function addBook(book: Omit<DbBook, 'id'>) {
  const db = getDb();
  const stmt = db.prepare(`
    INSERT INTO livres (titre, auteur, categorie, annee_publication, quantite, statut)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  stmt.run(book.titre, book.auteur, book.categorie, book.annee_publication, book.quantite, book.statut);
  revalidatePath('/');
}

export async function updateBook(id: number, book: Omit<DbBook, 'id'>) {
  const db = getDb();
  const stmt = db.prepare(`
    UPDATE livres
    SET titre = ?, auteur = ?, categorie = ?, annee_publication = ?, quantite = ?, statut = ?
    WHERE id = ?
  `);
  stmt.run(book.titre, book.auteur, book.categorie, book.annee_publication, book.quantite, book.statut, id);
  revalidatePath('/');
}

export async function deleteBook(id: number) {
  const db = getDb();
  const stmt = db.prepare('DELETE FROM livres WHERE id = ?');
  stmt.run(id);
  revalidatePath('/');
}
