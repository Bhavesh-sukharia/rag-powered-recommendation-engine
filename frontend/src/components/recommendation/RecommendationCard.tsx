import { Recommendation } from '@/types/recommendation';
import { useSimulatorStore } from '@/store/simulatorStore';

interface Props {
  recommendation: Recommendation;
  rank: number;
  averageUserRating: number;
  totalRecommendations: number;
}

export default function RecommendationCard({
  recommendation,
  rank,
  averageUserRating,
  totalRecommendations,
}: Props) {
  const movie = recommendation.movie;
  const options = useSimulatorStore((state) => state.options);

  return (
    <div className='rounded-2xl border bg-background p-5'>
      <div className='flex items-start gap-4'>
        <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-100 text-lg font-semibold text-violet-700 dark:bg-violet-950 dark:text-violet-200'>
          {movie.title.charAt(0).toUpperCase()}
        </div>

        <div className='flex-1'>
          <div className='flex items-center'>
            <div>
              <h3 className='text-lg font-semibold'>{movie.title}</h3>
              <p className='text-sm text-muted-foreground'>{movie.genres.join(' • ')}</p>
            </div>

            <div className='ml-auto text-right'>
              <div className='text-2xl font-bold text-violet-600'>
                {(recommendation.finalScore * 100).toFixed(0)}%
              </div>
              <div className='text-xs text-muted-foreground'>
                Rank #{rank + 1} of {totalRecommendations}
              </div>
            </div>
          </div>

          <div className='mt-5 grid grid-cols-4 gap-3'>
            <ScoreBox label='CF Score' value={recommendation.cfScore} />
            <ScoreBox label='CB Score' value={recommendation.cbScore} />
            <SentimentBox score={recommendation.sentimentScore} />
            <ScoreBox
              label='Avg Use Rating'
              value={averageUserRating}
              suffix='/5'
              highlight={averageUserRating > 0}
            />
          </div>

          <div className='mt-5 flex flex-wrap gap-2'>
            {(movie.aspects ?? []).map((aspect) => (
              <span
                key={aspect}
                className='rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700'
              >
                {aspect}
              </span>
            ))}
          </div>

          {options.ragExplanation && recommendation.ragExplanation ? (
            <div className='mt-5 rounded-xl border-l-4 border-violet-600 bg-muted p-4'>
              <div className='mb-2 text-[10px] font-semibold uppercase tracking-wide text-violet-600'>
                RAG Explanation
              </div>
              <p className='text-sm leading-relaxed text-muted-foreground'>
                {recommendation.ragExplanation}
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function ScoreBox({
  label,
  value,
  suffix = '',
  highlight = false,
}: {
  label: string;
  value: number;
  suffix?: string;
  highlight?: boolean;
}) {
  return (
    <div className='rounded-xl bg-muted p-3'>
      <div className='text-xs text-muted-foreground'>{label}</div>
      <div className={`mt-1 text-lg font-semibold ${highlight ? 'text-violet-600' : ''}`}>
        {value.toFixed(2)}{suffix}
      </div>
    </div>
  );
}

function SentimentBox({ score }: { score: number }) {
  const label = score >= 0.66 ? 'Highly praised' : score >= 0.34 ? 'Mixed Reviews' : 'Less Appreciated';

  return (
    <div className='rounded-xl bg-muted p-3'>
      <div className='text-xs text-muted-foreground'>Sentiment</div>
      <div className='mt-1 text-lg font-semibold'>{label}</div>
    </div>
  );
}
