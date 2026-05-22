import { Movie } from './movie';

export interface Recommendation {
  movie: Movie;
  cfScore: number;
  cbScore: number;
  sentimentLabel?: string | null;
  finalScore: number;
  ragExplanation: string;
}
