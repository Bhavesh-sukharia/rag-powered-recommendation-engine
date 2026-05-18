import React from 'react';
import UserList from '../users/UserList';
import { useSimulatorStore } from '@/store/simulatorStore';
import { apiClient } from '@/lib/api';

const AVAILABLE_GENRES = [
  'Action',
  'Adventure',
  'Animation',
  'Biography',
  'Comedy',
  'Crime',
  'Drama',
  'Fantasy',
  'Horror',
  'Mystery',
  'Romance',
  'Sci-Fi',
  'Thriller',
];

export default function Sidebar() {
  return (
    <aside className='flex w-[260px] flex-col gap-6 overflow-y-auto border-r bg-muted/30 p-4'>
      <UserList />

      <div>
        <h3 className='mb-3 text-xs uppercase tracking-wider text-muted-foreground'>
          Engine Weights
        </h3>

        <WeightsEditor />
      </div>
    </aside>
  );
}

function WeightsEditor() {
  const weights = useSimulatorStore((s) => s.weights);
  const setWeights = useSimulatorStore((s) => s.setWeights);
  const runRecommendations = useSimulatorStore((s) => s.runRecommendations);
  const options = useSimulatorStore((s) => s.options);
  const setOptions = useSimulatorStore((s) => s.setOptions);

  const adjust = (key: 'cf' | 'cb', value: number) => {
    value = Math.max(0, Math.min(100, Math.round(value)));
    const old = { ...weights } as { cf: number; cb: number };
    const remaining = 100 - value;

    const otherKey = key === 'cf' ? 'cb' : 'cf';
    const newOther = Math.round(remaining);

    const newWeights = {
      cf: key === 'cf' ? value : newOther,
      cb: key === 'cb' ? value : newOther,
    };

    setWeights(newWeights);
  };

  React.useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const wRes = await apiClient.get<{ weights?: { cf: number; cb: number; sentiment?: number } }>('/api/config/weights');
        const weights = wRes.data?.weights;
        if (mounted && weights) {
          setWeights({ cf: weights.cf, cb: weights.cb });
        }
      } catch (e) {
        // ignore
      }

      try {
        const oRes = await apiClient.get<{ options?: { sentimentRerank: boolean; ragExplanation: boolean } }>('/api/config/options');
        const options = oRes.data?.options;
        if (mounted && options) {
          setOptions({ sentimentRerank: options.sentimentRerank, ragExplanation: options.ragExplanation });
        }
      } catch (e) {
        // ignore
      }
    })();
    return () => {
      mounted = false;
    };
  }, [setWeights, setOptions]);

  return (
    <div className='space-y-4'>
      {([
        { key: 'cf', label: 'CF', color: 'bg-violet-600' },
        { key: 'cb', label: 'CB', color: 'bg-emerald-600' },
      ] as const).map(({ key, label, color }) => (
        <div key={key}>
          <div className='mb-1 flex justify-between text-sm'>
            <span>{label}</span>
            <span>{weights[key]}%</span>
          </div>
          <div className='flex items-center gap-3'>
            <input
              type='range'
              min={0}
              max={100}
              value={weights[key]}
              onChange={(e) => adjust(key as 'cf' | 'cb', Number(e.target.value))}
              className='h-2 flex-1 appearance-none rounded-lg bg-muted accent-violet-600'
            />
            <div className='w-12 text-right text-xs'>{weights[key]}%</div>
          </div>
          <div className='mt-2 h-2 overflow-hidden rounded bg-muted'>
            <div className={`${color} h-full`} style={{ width: `${weights[key]}%` }} />
          </div>
        </div>
      ))}

      <div className='mt-3 relative'>
        <SingleActionButton
          weights={weights}
          setWeights={setWeights}
          runRecommendations={runRecommendations}
        />
      </div>

      <div className='pt-2'>
        <h4 className='mb-2 text-xs uppercase tracking-wider text-muted-foreground'>Options</h4>

        <div className='space-y-2'>
          <ToggleRow
            label='Sentiment Re-rank'
            checked={options.sentimentRerank}
            onChange={async (checked) => {
              await setOptions({ sentimentRerank: checked });
              runRecommendations();
            }}
          />
          <ToggleRow
            label='RAG Explanation'
            checked={options.ragExplanation}
            onChange={async (checked) => {
              await setOptions({ ragExplanation: checked });
              runRecommendations();
            }}
          />
        </div>
      </div>

      <div className='pt-2'>
        <h4 className='mb-2 text-xs uppercase tracking-wider text-muted-foreground'>Genre Filter</h4>
        <GenreFilter />
      </div>

      <div className='pt-2'>
        <h4 className='mb-2 text-xs uppercase tracking-wider text-muted-foreground'>Rating Filter</h4>
        <RatingFilter />
      </div>
    </div>
  );
}

function GenreFilter() {
  const selectedGenres = useSimulatorStore((state) => state.filters.genres);
  const toggleFilterGenre = useSimulatorStore((state) => state.toggleFilterGenre);

  return (
    <div className='flex flex-wrap gap-2'>
      {AVAILABLE_GENRES.map((genre) => {
        const active = selectedGenres.includes(genre);
        return (
          <button
            key={genre}
            type='button'
            onClick={() => toggleFilterGenre(genre)}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
              active
                ? 'border-violet-600 bg-violet-600 text-white'
                : 'border-border bg-background text-foreground hover:border-violet-500'
            }`}
          >
            {genre}
          </button>
        );
      })}
    </div>
  );
}

function RatingFilter() {
  const minRating = useSimulatorStore((state) => state.filters.minRating);
  const setFilters = useSimulatorStore((state) => state.setFilters);

  return (
    <div className='space-y-2'>
      <div className='flex items-center justify-between text-sm'>
        <span>Min Rating</span>
        <span className='font-medium'>{minRating.toFixed(1)}/5</span>
      </div>
      <input
        type='range'
        min={0}
        max={5}
        step={0.5}
        value={minRating}
        onChange={(event) => setFilters({ minRating: Number(event.target.value) })}
        className='h-2 w-full appearance-none rounded-lg bg-muted accent-violet-600'
      />
      <div className='text-xs text-muted-foreground'>Only recommendations with average user rating at or above this value will show.</div>
    </div>
  );
}

function ToggleRow({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <button
      type='button'
      onClick={() => onChange(!checked)}
      className='flex w-full items-center justify-between rounded-xl border border-border bg-background px-3 py-2 text-left text-sm hover:bg-muted'
    >
      <span>{label}</span>
      <span
        className={`inline-flex h-6 w-11 items-center rounded-full p-1 transition ${
          checked ? 'bg-violet-600' : 'bg-muted-foreground/30'
        }`}
      >
        <span
          className={`h-4 w-4 rounded-full bg-white transition ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </span>
    </button>
  );
}

function SingleActionButton({
  weights,
  setWeights,
  runRecommendations,
}: {
  weights: { cf: number; cb: number; sentiment?: number };
  setWeights: (w: { cf: number; cb: number; sentiment?: number }) => void;
  runRecommendations: () => void;
}) {
  const handleClick = async () => {
    try {
      // Attempt to save current weights to backend
      const res = await apiClient.post('/api/config/weights', weights);
      if (res.status >= 200 && res.status < 300) {
        const data = res.data;
        if (data?.weights) {
          // use server-normalized weights
          setWeights(data.weights);
        }
      } else {
        // eslint-disable-next-line no-console
        console.error('Save failed', res.statusText || res.status);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Save request error', err);
    } finally {
      // Always refresh recommendations so UI repopulates
      runRecommendations();
    }
  };

  return (
    <div>
      <button
        type='button'
        onClick={handleClick}
        className='w-full rounded-lg bg-violet-600 px-3 py-2 text-sm font-medium text-white hover:bg-violet-700'
      >
        Save & Reset
      </button>
    </div>
  );
}
