import { Movie } from './movie';

export interface Recommendation {
  movie: Movie;
  cfScore: number;
  cbScore: number;
  sentimentScore: number;
  finalScore: number;
  ragExplanation: string;
}
