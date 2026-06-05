'use client';

import { Search, Bell } from 'lucide-react';

export default function SearchHeader() {
  return (
    <header className="w-full flex items-center justify-between px-8 py-5">
      {/* Left side */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Welcome back, Hiba</h1>
        <p className="text-sm text-gray-400 mt-1">What would you like to read today?</p>
      </div>

      {/* Center - Search bar */}
      <div className="relative flex items-center w-[420px]">
        <Search className="absolute left-4 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search your favourite books"
          className="w-full bg-gray-50 border-0 rounded-2xl pl-12 pr-4 py-3.5 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:bg-white transition-all"
        />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Notification bell */}
        <div className="relative w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center hover:bg-gray-100 transition-colors cursor-pointer">
          <Bell className="w-5 h-5 text-gray-600" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full" />
        </div>

        {/* User avatar */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center cursor-pointer">
          <span className="text-white font-semibold text-sm">HD</span>
        </div>
      </div>
    </header>
  );
}
