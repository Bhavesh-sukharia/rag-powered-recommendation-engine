import { useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import MovieGrid from '@/components/movie/MovieGrid';
import RecommendationList from '@/components/recommendation/RecommendationList';
import StatsGrid from '@/components/stats/StatsGrid';
import UsersPanel from '@/components/users/UsersPanel';
import { useSimulatorStore } from '@/store/simulatorStore';

export default function SimulatorPage() {
  const activeTab = useSimulatorStore((state) => state.activeTab);
  const loadUsers = useSimulatorStore((state) => state.loadUsers);
  const loadMovies = useSimulatorStore((state) => state.loadMovies);
  const loadMovieCount = useSimulatorStore((state) => state.loadMovieCount);
  const runRecommendations = useSimulatorStore((state) => state.runRecommendations);

  // Run recommendations on component mount
  useEffect(() => {
    void (async () => {
      await loadUsers();
      await loadMovies();
      if (typeof loadMovieCount === 'function') {
        // attempt to fetch total count explicitly (some store setups may fetch automatically)
        try {
          await loadMovieCount();
        } catch (e) {
          // ignore
        }
      }
      await runRecommendations();
    })();
  }, [loadMovies, loadUsers, runRecommendations]);

  return (
    <MainLayout>
      {activeTab === 'recommendations' && (
        <>
          <StatsGrid />
          <RecommendationList />
        </>
      )}

      {activeTab === 'catalog' && <MovieGrid />}
      {activeTab === 'users' && <UsersPanel />}
    </MainLayout>
  );
}
