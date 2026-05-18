import { Check, Star, X } from 'lucide-react';

import { Movie } from '@/types/movie';
import { useSimulatorStore } from '@/store/simulatorStore';

interface Props {
  movie: Movie;
  averageRating: number;
  ratedByCount: number;
}

export default function MovieCard({ movie, averageRating, ratedByCount }: Props) {
  const users = useSimulatorStore((state) => state.users);
  const activeUserId = useSimulatorStore((state) => state.activeUserId);
  const pendingRating = useSimulatorStore((state) => state.pendingRating);
  const selectRating = useSimulatorStore((state) => state.selectRating);
  const confirmRating = useSimulatorStore((state) => state.confirmRating);
  const discardRating = useSimulatorStore((state) => state.discardRating);

  const activeUser = users.find((user) => user.id === activeUserId);
  const isPending = pendingRating?.movieId === movie.id;
  const activeUserRating = activeUser?.ratings[movie.id] ?? 0;
  const currentStars = isPending ? pendingRating.stars : activeUserRating;

  return (
    <div className='rounded-2xl border bg-background p-4'>
      <div className='mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-100 text-lg font-semibold text-violet-700 dark:bg-violet-950 dark:text-violet-200'>
        {movie.title.charAt(0).toUpperCase()}
      </div>
      <h3 className='font-medium'>{movie.title}</h3>
      <p className='mt-1 text-xs text-muted-foreground'>{movie.genres.join(' • ')}</p>

      {movie.overview ? (
        <p className='mt-3 line-clamp-3 text-xs leading-relaxed text-muted-foreground'>
          {movie.overview}
        </p>
      ) : null}

      <div className='mt-3 rounded-xl bg-muted/40 px-3 py-2 text-xs text-muted-foreground'>
        <div className='flex items-center justify-between gap-2'>
          <span>Avg rating</span>
          <span className='font-semibold text-foreground'>{averageRating ? averageRating.toFixed(1) : '0.0'}/5</span>
        </div>
        <div className='mt-1 flex items-center justify-between gap-2'>
          <span>Rated by</span>
          <span className='font-semibold text-foreground'>{ratedByCount} user{ratedByCount === 1 ? '' : 's'}</span>
        </div>
      </div>

      <div className='mt-4 flex items-center justify-between gap-3'>
        <div className='flex items-center gap-1'>
          {[1, 2, 3, 4, 5].map((star) => {
            const isSelected = star <= currentStars;

            return (
              <button
                key={star}
                type='button'
                onClick={() => selectRating(movie.id, star)}
                className='rounded-full p-0.5 transition hover:bg-muted'
                aria-label={`Rate ${movie.title} ${star} stars`}
              >
                <Star className={`h-4 w-4 ${isSelected ? 'fill-amber-500 text-amber-500' : 'text-muted-foreground'}`} />
              </button>
            );
          })}
        </div>

        {isPending && (
          <div className='flex items-center gap-1'>
            <button
              type='button'
              onClick={discardRating}
              className='grid h-6 w-6 place-items-center rounded-full bg-red-500 text-white transition hover:bg-red-600'
              aria-label='Discard rating change'
            >
              <X className='h-3.5 w-3.5' />
            </button>
            <button
              type='button'
              onClick={confirmRating}
              className='grid h-6 w-6 place-items-center rounded-full bg-emerald-500 text-white transition hover:bg-emerald-600'
              aria-label='Confirm rating change'
            >
              <Check className='h-3.5 w-3.5' />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
