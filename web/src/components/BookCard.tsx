'use client';

import { BookOpen } from 'lucide-react';
import { DbBook } from '@/app/actions';

interface BookCardProps {
  book: DbBook;
  onClick?: () => void;
  isSelected?: boolean;
}

export default function BookCard({
  book,
  onClick,
  isSelected,
}: BookCardProps) {
  const isAvailable = book.statut === 'disponible';
  const isBorrowed = book.statut === 'emprunté';

  return (
    <div
      className="group cursor-pointer transition-all duration-300 hover:-translate-y-2"
      onClick={onClick}
    >
      <div
        className={`relative overflow-hidden rounded-2xl aspect-[2/3] mb-4 bg-gradient-to-br from-blue-50 to-white border shadow-sm flex items-center justify-center group-hover:shadow-lg transition-all duration-300 ${
          isSelected ? 'ring-2 ring-blue-500 ring-offset-2 border-transparent' : 'border-gray-100'
        }`}
      >
        <BookOpen className="w-12 h-12 text-blue-200" />
        
        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
            isAvailable ? 'bg-green-100 text-green-700' : 
            isBorrowed ? 'bg-orange-100 text-orange-700' : 
            'bg-purple-100 text-purple-700'
          }`}>
            {book.statut}
          </span>
        </div>
      </div>

      <h3 className="text-sm font-semibold text-gray-900 line-clamp-1">
        {book.titre}
      </h3>
      <p className="text-xs text-gray-400 mt-1">{book.auteur}</p>
      <div className="flex items-center gap-2 mt-2">
        <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">{book.categorie}</span>
        <span className="text-xs text-gray-400">Exemplaires: {book.quantite}</span>
      </div>
    </div>
  );
}
