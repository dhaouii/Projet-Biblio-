'use client';

import { BookOpen, MapPin, Hash, Bookmark } from 'lucide-react';
import { DbBook } from '@/app/actions';

interface BookDetailsPanelProps {
  book: DbBook | null;
}

export default function BookDetailsPanel({ book }: BookDetailsPanelProps) {
  if (!book) {
    return (
      <div className="w-[380px] min-h-screen bg-gradient-to-b from-[#001B5E] to-[#001040] text-white p-8 flex flex-col items-center justify-center rounded-l-3xl">
        <BookOpen className="w-16 h-16 text-blue-300/40 mb-4" />
        <p className="text-blue-200/50 text-sm">Sélectionnez un livre pour voir les détails</p>
      </div>
    );
  }

  const isAvailable = book.statut === 'disponible';

  return (
    <div className="w-[380px] min-h-screen bg-gradient-to-b from-[#001B5E] to-[#001040] text-white p-8 flex flex-col rounded-l-3xl">
      <p className="text-xs uppercase tracking-widest text-blue-300/60 font-semibold mb-8">
        Détails du Livre
      </p>

      <div className="relative w-48 h-72 mx-auto mb-8 rounded-2xl overflow-hidden shadow-2xl shadow-black/40 bg-white/5 border border-white/10 flex items-center justify-center">
        <div className="absolute -inset-4 bg-blue-500/20 blur-3xl rounded-full -z-10" />
        <BookOpen className="w-20 h-20 text-blue-300/50" />
      </div>

      <h2 className="text-xl font-bold text-center">{book.titre}</h2>
      <p className="text-sm text-blue-200/70 text-center mt-1">{book.auteur}</p>

      <div className="flex items-center justify-center gap-2 mt-4">
        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
          isAvailable ? 'bg-green-500/20 text-green-300' : 
          book.statut === 'emprunté' ? 'bg-orange-500/20 text-orange-300' : 
          'bg-purple-500/20 text-purple-300'
        }`}>
          {book.statut}
        </span>
      </div>

      <div className="flex flex-col gap-4 mt-8 bg-white/5 rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-200/60">
            <Hash className="w-4 h-4" />
            <span className="text-sm">ID Livre</span>
          </div>
          <span className="text-sm font-medium">{book.id}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-200/60">
            <Bookmark className="w-4 h-4" />
            <span className="text-sm">Catégorie</span>
          </div>
          <span className="text-sm font-medium">{book.categorie}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-200/60">
            <BookOpen className="w-4 h-4" />
            <span className="text-sm">Année</span>
          </div>
          <span className="text-sm font-medium">{book.annee_publication}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-200/60">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">Exemplaires</span>
          </div>
          <span className="text-sm font-medium">{book.quantite}</span>
        </div>
      </div>
    </div>
  );
}
