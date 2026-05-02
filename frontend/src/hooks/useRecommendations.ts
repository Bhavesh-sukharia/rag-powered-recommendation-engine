import { useEffect, useState } from 'react';

import { fetchRecommendations } from '../api/client';


export function useRecommendations(userId: string, query: string) {
  const [items, setItems] = useState<Array<{ item_id: string; score: number }>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);

    fetchRecommendations(userId, query)
      .then((data) => {
        if (active) {
          setItems(data.items);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [userId, query]);

  return { items, loading };
}