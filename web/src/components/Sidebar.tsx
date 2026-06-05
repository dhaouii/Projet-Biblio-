'use client';

import {
  BookOpen,
  Library,
  Settings,
  HelpCircle,
  Database,
  LayoutDashboard,
  ShieldAlert,
  User
} from 'lucide-react';

export type PageId = 'Dashboard' | 'Catalogue' | 'Gestion' | 'Settings' | 'Support';
export type Role = 'admin' | 'user';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, adminOnly: false },
  { label: 'Catalogue', icon: Library, adminOnly: false },
  { label: 'Gestion', icon: Database, adminOnly: true },
] as const;

const bottomItems = [
  { label: 'Settings', icon: Settings },
  { label: 'Support', icon: HelpCircle },
] as const;

interface SidebarProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
  role: Role;
  onRoleChange: (role: Role) => void;
}

export default function Sidebar({ activePage, onNavigate, role, onRoleChange }: SidebarProps) {
  return (
    <aside className="w-[260px] h-screen bg-white border-r border-gray-100 p-6 flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-md shadow-blue-200">
            <BookOpen className="h-5 w-5 text-white" strokeWidth={1.75} />
          </div>
          <span className="text-xl font-bold text-gray-900">BiblioTech</span>
        </div>
        <p className="mt-1.5 pl-[52px] text-xs text-gray-400">Gestion de Bibliothèque</p>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1">
        {navItems.map(({ label, icon: Icon, adminOnly }) => {
          if (adminOnly && role !== 'admin') return null;
          
          const isActive = activePage === label;
          return (
            <button
              key={label}
              onClick={() => onNavigate(label as PageId)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
              }`}
            >
              <Icon className="h-5 w-5" strokeWidth={1.75} />
              {label}
            </button>
          );
        })}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Role Toggle Profile Card */}
      <div className="mb-4 bg-gray-50 rounded-xl p-3 border border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${role === 'admin' ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'}`}>
            {role === 'admin' ? <ShieldAlert className="w-4 h-4" /> : <User className="w-4 h-4" />}
          </div>
          <div className="flex flex-col text-left">
            <span className="text-xs font-bold text-gray-900 uppercase tracking-wide">Profil</span>
            <span className="text-[11px] font-medium text-gray-500">{role === 'admin' ? 'Administrateur' : 'Lecteur'}</span>
          </div>
        </div>
        <button 
          onClick={() => {
            onRoleChange(role === 'admin' ? 'user' : 'admin');
            if (role === 'admin' && activePage === 'Gestion') {
              onNavigate('Dashboard');
            }
          }}
          className="text-[10px] font-bold text-gray-500 bg-white border border-gray-200 px-2 py-1 rounded hover:bg-gray-100 transition-colors cursor-pointer"
        >
          CHANGER
        </button>
      </div>

      {/* Bottom section */}
      <div className="border-t border-gray-100 pt-4 flex flex-col gap-1">
        {bottomItems.map(({ label, icon: Icon }) => (
          <button
            key={label}
            onClick={() => onNavigate(label as PageId)}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer text-gray-400 ${
              activePage === label
                ? 'bg-blue-50 text-blue-600'
                : 'hover:bg-gray-50 hover:text-gray-700'
            }`}
          >
            <Icon className="h-5 w-5" strokeWidth={1.75} />
            {label}
          </button>
        ))}
      </div>
    </aside>
  );
}
