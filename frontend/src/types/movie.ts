export interface Movie {
  id: number;
  item_id?: number;
  title: string;
  genres: string[];
  overview?: string | null;
  avg_rating?: number | null;
  rating_number?: number | null;
  created_at?: string;
  sentiment_label?: string | null;
}
