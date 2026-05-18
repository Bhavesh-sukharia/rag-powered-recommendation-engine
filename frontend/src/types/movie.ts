export interface Movie {
  id: number;
  item_id?: number;
  title: string;
  genres: string[];
  overview?: string | null;
  avg_rating?: number | null;
  rating_number?: number | null;
  created_at?: string;
  emoji?: string;
  sentiment?: number;
  aspects?: string[];
  cf_base?: number;
  cb_tags?: string[];
}
