'use client';

import { useState } from 'react';
import { DbBook, addBook, updateBook, deleteBook } from '@/app/actions';
import { Pencil, Trash2, Plus, X, Search } from 'lucide-react';

interface BookManagerProps {
  initialBooks: DbBook[];
}

export default function BookManager({ initialBooks }: BookManagerProps) {
  const [books, setBooks] = useState<DbBook[]>(initialBooks);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<DbBook | null>(null);

  // Form state
  const [titre, setTitre] = useState('');
  const [auteur, setAuteur] = useState('');
  const [categorie, setCategorie] = useState('');
  const [annee, setAnnee] = useState(new Date().getFullYear());
  const [quantite, setQuantite] = useState(1);
  const [statut, setStatut] = useState<'disponible' | 'emprunté' | 'réservé'>('disponible');

  const filteredBooks = books.filter(b => 
    b.titre.toLowerCase().includes(search.toLowerCase()) || 
    b.auteur.toLowerCase().includes(search.toLowerCase()) ||
    b.id.toString() === search
  );

  const openModal = (book?: DbBook) => {
    if (book) {
      setEditingBook(book);
      setTitre(book.titre);
      setAuteur(book.auteur);
      setCategorie(book.categorie);
      setAnnee(book.annee_publication);
      setQuantite(book.quantite);
      setStatut(book.statut);
    } else {
      setEditingBook(null);
      setTitre('');
      setAuteur('');
      setCategorie('Roman');
      setAnnee(new Date().getFullYear());
      setQuantite(1);
      setStatut('disponible');
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingBook(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const bookData = { titre, auteur, categorie, annee_publication: annee, quantite, statut };
    
    if (editingBook) {
      await updateBook(editingBook.id, bookData);
      setBooks(books.map(b => b.id === editingBook.id ? { ...bookData, id: editingBook.id } : b));
    } else {
      // Optistic UI update will be overwritten on refresh, but good for UX
      await addBook(bookData);
      // Force reload to get the real ID from server
      window.location.reload(); 
    }
    closeModal();
  };

  const handleDelete = async (id: number) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce livre ?')) {
      await deleteBook(id);
      setBooks(books.filter(b => b.id !== id));
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      {/* Toolbar */}
      <div className="p-6 border-b border-gray-100 flex items-center justify-between gap-4 bg-gray-50/50">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher par titre, auteur ou ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Ajouter un livre
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 font-semibold">ID</th>
              <th className="px-6 py-4 font-semibold">Titre & Auteur</th>
              <th className="px-6 py-4 font-semibold">Catégorie</th>
              <th className="px-6 py-4 font-semibold">Année</th>
              <th className="px-6 py-4 font-semibold">Qté</th>
              <th className="px-6 py-4 font-semibold">Statut</th>
              <th className="px-6 py-4 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredBooks.map((book) => (
              <tr key={book.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4 text-gray-500 font-medium">#{book.id}</td>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{book.titre}</div>
                  <div className="text-gray-400 text-xs mt-0.5">{book.auteur}</div>
                </td>
                <td className="px-6 py-4">
                  <span className="bg-gray-100 text-gray-600 px-2.5 py-1 rounded-md text-xs font-medium">
                    {book.categorie}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-500">{book.annee_publication}</td>
                <td className="px-6 py-4 font-medium">{book.quantite}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    book.statut === 'disponible' ? 'bg-green-100 text-green-700' : 
                    book.statut === 'emprunté' ? 'bg-orange-100 text-orange-700' : 
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {book.statut}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button 
                      onClick={() => openModal(book)}
                      className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => handleDelete(book.id)}
                      className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filteredBooks.length === 0 && (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-400">
                  Aucun livre trouvé.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Form */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="text-lg font-bold text-gray-900">
                {editingBook ? 'Modifier le livre' : 'Ajouter un livre'}
              </h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Titre</label>
                <input required type="text" value={titre} onChange={e => setTitre(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Auteur</label>
                <input required type="text" value={auteur} onChange={e => setAuteur(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
                  <input required type="text" value={categorie} onChange={e => setCategorie(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Année</label>
                  <input required type="number" value={annee} onChange={e => setAnnee(parseInt(e.target.value))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantité</label>
                  <input required type="number" min="1" value={quantite} onChange={e => setQuantite(parseInt(e.target.value))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Statut</label>
                  <select value={statut} onChange={e => setStatut(e.target.value as any)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white">
                    <option value="disponible">Disponible</option>
                    <option value="emprunté">Emprunté</option>
                    <option value="réservé">Réservé</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <button type="button" onClick={closeModal} className="flex-1 px-4 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors cursor-pointer">
                  Annuler
                </button>
                <button type="submit" className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 shadow-sm shadow-blue-200 transition-colors cursor-pointer">
                  {editingBook ? 'Sauvegarder' : 'Ajouter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
