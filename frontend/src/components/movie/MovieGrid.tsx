import { useEffect, useRef, useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

import { useSimulatorStore } from '@/store/simulatorStore';

import MovieCard from './MovieCard';

export default function MovieGrid() {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const sentinelRef = useRef<HTMLDivElement>(null);
  const movies = useSimulatorStore((state) => state.movies);
  const loadMovies = useSimulatorStore((state) => state.loadMovies);
  const loadMoreMovies = useSimulatorStore((state) => state.loadMoreMovies);
  const searchMovies = useSimulatorStore((state) => state.searchMovies);
  const loadMoreSearchMovies = useSimulatorStore((state) => state.loadMoreSearchMovies);
  const isLoadingMoreMovies = useSimulatorStore((state) => state.isLoadingMoreMovies);
  const isSearchingMovies = useSimulatorStore((state) => state.isSearchingMovies);
  const users = useSimulatorStore((state) => state.users);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearchTerm(searchTerm.trim());
    }, 350);

    return () => window.clearTimeout(timeoutId);
  }, [searchTerm]);

  useEffect(() => {
    if (!debouncedSearchTerm) {
      void loadMovies();
      return;
    }

    void searchMovies({ query: debouncedSearchTerm, page: 1, limit: 20, sort: 'rating' });
  }, [debouncedSearchTerm, loadMovies, searchMovies]);

  // Intersection observer for infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          if (debouncedSearchTerm) {
            void loadMoreSearchMovies();
          } else {
            void loadMoreMovies();
          }
        }
      },
      { threshold: 0.1 }
    );

    if (sentinelRef.current) {
      observer.observe(sentinelRef.current);
    }

    return () => observer.disconnect();
  }, [loadMoreMovies]);

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
  };

  const isLoadingBottom = isLoadingMoreMovies || isSearchingMovies;

  return (
    <div className='relative space-y-4 pb-24'>
      <div className='relative'>
        <Search className='pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground' />
        <input
          type='search'
          value={searchTerm}
          onChange={(event) => handleSearchChange(event.target.value)}
          placeholder='Search movies by title or genre'
          className='w-full rounded-2xl border bg-background py-3 pl-11 pr-4 text-sm outline-none transition placeholder:text-muted-foreground focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:focus:ring-violet-900'
        />
      </div>

      <div className='grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4'>
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            averageRating={movie.avg_rating ?? 0}
            ratedByCount={movie.rating_number ?? 0}
          />
        ))}
      </div>

      {/* Infinite scroll sentinel */}
      <div ref={sentinelRef} className='h-1' aria-hidden='true' />

      {isLoadingBottom && (
        <div className='pointer-events-none fixed bottom-6 left-1/2 z-30 -translate-x-1/2'>
          <div className='flex items-center gap-2 rounded-full border border-border bg-background/95 px-4 py-2 shadow-lg' aria-live='polite'>
            <Loader2 className='h-5 w-5 animate-spin text-violet-600' />
            <span className='text-sm text-muted-foreground'>Loading more movies...</span>
          </div>
        </div>
      )}
    </div>
  );
}
