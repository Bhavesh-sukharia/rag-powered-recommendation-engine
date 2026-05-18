import { MOVIES } from '@/mock/movies';

import ReviewCard from './ReviewCard';

export default function ReviewList() {
  return (
    <div className='space-y-4'>
      {MOVIES.map((movie) => (
        <ReviewCard key={movie.id} movie={movie} />
      ))}
    </div>
  );
}
