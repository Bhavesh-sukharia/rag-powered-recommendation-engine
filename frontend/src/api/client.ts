import axios from 'axios';


const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
});

export async function fetchRecommendations(userId: string, query = '') {
  const response = await api.post('/api/v1/recommend', {
    user_id: userId,
    query,
    limit: 6,
  });
  return response.data as { items: Array<{ item_id: string; score: number }> };
}

export async function fetchWhy(itemId: string) {
  const response = await api.get(`/api/v1/explanations/${itemId}`);
  return response.data as { explanation: string };
}