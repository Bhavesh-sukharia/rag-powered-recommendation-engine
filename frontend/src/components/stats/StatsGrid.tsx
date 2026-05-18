import { useSimulatorStore } from '@/store/simulatorStore';

export default function StatsGrid() {
  const users = useSimulatorStore((state) => state.users);
   const totalUserCount = useSimulatorStore((state) => (state as any).totalUserCount ?? users.length);
  const movies = useSimulatorStore((state) => state.movies);
  const totalMovieCount = useSimulatorStore((state) => (state as any).totalMovieCount ?? 0);
  const recommendations = useSimulatorStore((state) => state.recommendations);
  const selectedGenres = useSimulatorStore((state) => state.filters.genres);
  const minRating = useSimulatorStore((state) => state.filters.minRating);

  // Calculate filtered recommendations count (respects genre and rating filters)
  const filteredCount = recommendations.filter((recommendation) => {
    const matchesGenre =
      selectedGenres.length === 0 ||
      recommendation.movie.genres.some((genre) => selectedGenres.includes(genre));
    const averageUserRating = getAverageUserRating(users, recommendation.movie.id);
    const matchesRating = averageUserRating >= minRating;
    return matchesGenre && matchesRating;
  }).length;

  const totalRatings = users.reduce((total, user) => total + Object.keys(user.ratings).length, 0);

  return (
    <div className='mb-6 grid grid-cols-2 gap-4 xl:grid-cols-4'>
      <StatBox label='Users' value={totalUserCount} />
      <StatBox label='Movies' value={totalMovieCount} />
      <StatBox label='Ratings' value={totalRatings} />
      <StatBox label='Recommendations' value={filteredCount} />
    </div>
  );
}

function getAverageUserRating(users: Array<{ ratings: Record<number, number> }>, movieId: number) {
  const ratings = users
    .map((user) => user.ratings[movieId])
    .filter((rating): rating is number => typeof rating === 'number');

  if (!ratings.length) return 0;

  return ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length;
}

function StatBox({ label, value }: { label: string; value: number }) {
  return (
    <div className='rounded-2xl border bg-muted/40 p-5'>
      <div className='text-3xl font-bold'>{value}</div>
      <div className='mt-1 text-sm text-muted-foreground'>{label}</div>
    </div>
  );
}
