import { getBooks, getStats } from './actions';
import DashboardClient from './DashboardClient';

// Server Component
export default async function Home() {
  const books = await getBooks();
  const stats = await getStats();

  return <DashboardClient books={books} stats={stats} />;
}
