'use client';

import { useState } from 'react';
import { DbBook, LibraryStats } from '@/app/actions';
import Sidebar, { PageId, Role } from '@/components/Sidebar';
import SearchHeader from '@/components/SearchHeader';
import BookCard from '@/components/BookCard';
import BookDetailsPanel from '@/components/BookDetailsPanel';
import BookManager from '@/components/BookManager';
import AIChat from '@/components/AIChat';
import { BookOpen, Library, CheckCircle2, Search, Filter } from 'lucide-react';

interface DashboardClientProps {
  books: DbBook[];
  stats: LibraryStats;
}

export default function DashboardClient({ books, stats }: DashboardClientProps) {
  const [activePage, setActivePage] = useState<PageId>('Dashboard');
  const [selectedBook, setSelectedBook] = useState<DbBook | null>(null);
  const [role, setRole] = useState<Role>('user');

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('All');
  const [filterStatus, setFilterStatus] = useState<string>('All');
  const [filterYear, setFilterYear] = useState<string>('All');

  const uniqueCategories = Array.from(new Set(books.map(b => b.categorie))).sort();
  const uniqueYears = Array.from(new Set(books.map(b => b.annee_publication))).sort((a,b) => b - a);

  const filteredCatalogueBooks = books.filter(book => {
    const matchSearch = book.titre.toLowerCase().includes(searchQuery.toLowerCase()) || 
                        book.auteur.toLowerCase().includes(searchQuery.toLowerCase());
    const matchCategory = filterCategory === 'All' || book.categorie === filterCategory;
    const matchStatus = filterStatus === 'All' || book.statut === filterStatus;
    const matchYear = filterYear === 'All' || book.annee_publication.toString() === filterYear;
    return matchSearch && matchCategory && matchStatus && matchYear;
  });

  const renderContent = () => {
    switch (activePage) {
      case 'Dashboard':
        return (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Vue d'ensemble</h2>
            
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
                  <Library className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Total des livres</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                </div>
              </div>
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Disponibles</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.disponibles}</p>
                </div>
              </div>
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center">
                  <BookOpen className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Empruntés</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.empruntes}</p>
                </div>
              </div>
            </div>

            {/* Récemment ajoutés */}
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">Derniers ajouts</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {books.slice(0, 5).map((book) => (
                  <BookCard
                    key={book.id}
                    book={book}
                    onClick={() => setSelectedBook(book)}
                    isSelected={selectedBook?.id === book.id}
                  />
                ))}
              </div>
            </div>
          </div>
        );

      case 'Catalogue':
        return (
          <section className="flex flex-col h-full">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Catalogue complet</h2>
            <p className="text-gray-400 text-sm mb-6">Parcourez les {books.length} livres de la bibliothèque</p>
            
            {/* Filters Toolbar */}
            <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm mb-8 flex flex-wrap gap-4 items-center">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher titre ou auteur..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all"
                />
              </div>
              
              <div className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-xl border border-gray-200">
                <Filter className="w-4 h-4 text-gray-400" />
                <select 
                  value={filterCategory} 
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="bg-transparent text-sm font-medium text-gray-700 focus:outline-none cursor-pointer"
                >
                  <option value="All">Toutes les catégories</option>
                  {uniqueCategories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                </select>
              </div>

              <select 
                value={filterStatus} 
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-gray-50 px-3 py-2 rounded-xl border border-gray-200 text-sm font-medium text-gray-700 focus:outline-none cursor-pointer"
              >
                <option value="All">Tous les statuts</option>
                <option value="disponible">Disponible</option>
                <option value="emprunté">Emprunté</option>
                <option value="réservé">Réservé</option>
              </select>

              <select 
                value={filterYear} 
                onChange={(e) => setFilterYear(e.target.value)}
                className="bg-gray-50 px-3 py-2 rounded-xl border border-gray-200 text-sm font-medium text-gray-700 focus:outline-none cursor-pointer"
              >
                <option value="All">Toutes les années</option>
                {uniqueYears.map(year => <option key={year} value={year.toString()}>{year}</option>)}
              </select>
            </div>

            {/* Books Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {filteredCatalogueBooks.map((book) => (
                <BookCard
                  key={book.id}
                  book={book}
                  onClick={() => setSelectedBook(book)}
                  isSelected={selectedBook?.id === book.id}
                />
              ))}
              {filteredCatalogueBooks.length === 0 && (
                <div className="col-span-full py-12 text-center text-gray-400 bg-white rounded-2xl border border-gray-100 border-dashed">
                  Aucun livre ne correspond à vos filtres.
                </div>
              )}
            </div>
          </section>
        );

      case 'Gestion':
        if (role !== 'admin') return null;
        return (
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Gestion des livres</h2>
            <p className="text-gray-400 text-sm mb-8">Ajouter, modifier ou supprimer des livres (Accès Administrateur)</p>
            <BookManager initialBooks={books} />
          </section>
        );

      default:
        return (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <h3 className="text-lg font-semibold text-gray-400 mb-2">Section en construction</h3>
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50/80 overflow-hidden">
      <Sidebar 
        activePage={activePage} 
        onNavigate={setActivePage} 
        role={role}
        onRoleChange={setRole}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <SearchHeader />
        <main className="flex-1 overflow-y-auto px-8 pb-8">
          {renderContent()}
        </main>
      </div>

      {/* Details panel only shown for Dashboard and Catalogue */}
      {(activePage === 'Dashboard' || activePage === 'Catalogue') && (
        <BookDetailsPanel book={selectedBook} />
      )}

      {/* Floating Chatbot */}
      <AIChat />
    </div>
  );
}
