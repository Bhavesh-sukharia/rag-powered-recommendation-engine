import { useState } from 'react';

import { Movie } from '@/types/movie';
import { useSimulatorStore } from '@/store/simulatorStore';

interface Props {
  movie: Movie;
}

export default function ReviewCard({ movie }: Props) {
  const [text, setText] = useState('');
  const addReview = useSimulatorStore((state) => state.addReview);

  return (
    <div className='rounded-2xl border p-5'>
      <div className='mb-4 flex items-center gap-3'>
        <div className='text-2xl'>{movie.emoji}</div>
        <div>
          <h3 className='font-medium'>{movie.title}</h3>
          <p className='text-xs text-muted-foreground'>{movie.genres.join(' • ')}</p>
        </div>
      </div>

      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        className='min-h-[100px] w-full rounded-xl border bg-background p-3 text-sm'
        placeholder='Write review...'
      />

      <button
        type='button'
        onClick={() => addReview(movie.id, text)}
        className='mt-4 rounded-lg bg-violet-600 px-4 py-2 text-sm text-white hover:bg-violet-700'
      >
        Save Review
      </button>
    </div>
  );
}
