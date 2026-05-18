export interface User {
  id: number;
  apiId?: string;
  name: string;
  tastes: string[];
  ratings: Record<number, number>;
  reviews: Record<number, string>;
}
