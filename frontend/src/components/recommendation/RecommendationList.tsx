import RecommendationCard from './RecommendationCard';

import { useSimulatorStore } from '@/store/simulatorStore';

export default function RecommendationList() {
  const recommendations = useSimulatorStore((state) => state.recommendations);
  const users = useSimulatorStore((state) => state.users);
  const selectedGenres = useSimulatorStore((state) => state.filters.genres);
  const minRating = useSimulatorStore((state) => state.filters.minRating);

  const filteredRecommendations = recommendations
    .map((recommendation) => ({
      recommendation,
      averageUserRating:
        (recommendation.movie.avg_rating ?? null) !== null
          ? (recommendation.movie.avg_rating as number)
          : getAverageUserRating(users, recommendation.movie.id),
    }))
    .filter(({ recommendation, averageUserRating }) => {
    const matchesGenre =
      selectedGenres.length === 0 ||
      recommendation.movie.genres.some((genre) => selectedGenres.includes(genre));
    const matchesRating = averageUserRating >= minRating;

    return matchesGenre && matchesRating;
    });

  if (!recommendations.length) {
    return (
      <div className='flex h-[400px] items-center justify-center text-muted-foreground'>
        Loading your recommendations.
      </div>
    );
  }

  if (!filteredRecommendations.length) {
    return (
      <div className='flex h-[400px] items-center justify-center text-muted-foreground'>
        No recommendations match the current genre or rating filters.
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {filteredRecommendations.map(({ recommendation, averageUserRating }, index) => (
        <RecommendationCard
          key={recommendation.movie.id}
          recommendation={recommendation}
          rank={index}
          averageUserRating={averageUserRating}
          totalRecommendations={filteredRecommendations.length}
        />
      ))}
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
