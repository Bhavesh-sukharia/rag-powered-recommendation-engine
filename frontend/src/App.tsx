import { useState } from 'react';

import { fetchWhy } from './api/client';
import RecommendationCard from './components/RecommendationCard';
import UserPicker from './components/UserPicker';
import { useRecommendations } from './hooks/useRecommendations';


export default function App() {
  const [userId, setUserId] = useState('user-001');
  const [query, setQuery] = useState('');
  const { items, loading } = useRecommendations(userId, query);

  const handleWhy = async (itemId: string) => {
    const { explanation } = await fetchWhy(itemId);
    window.alert(explanation);
  };

  return (
    <main className="app-shell">
      <div className="app-container">
        <section className="hero">
          <span className="badge">Hybrid RecSys + RAG</span>
          <h1>Personalized recommendations with explainable ranking.</h1>
          <p>
            Explore a recommendation flow that blends collaborative filtering, content signals,
            sentiment-aware reranking, and retrieval-augmented explanations.
          </p>
        </section>

        <section className="panel">
          <div className="section-heading">
            <h2>Session controls</h2>
            <span>{loading ? 'Loading recommendations…' : 'Ready'}</span>
          </div>
          <div className="controls">
            <UserPicker value={userId} onChange={setUserId} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search a preference or mood"
            />
            <select defaultValue="hybrid">
              <option value="hybrid">Hybrid ranking</option>
              <option value="cf">Collaborative filtering</option>
              <option value="cb">Content based</option>
            </select>
          </div>
        </section>

        <section className="panel">
          <div className="section-heading">
            <h2>Recommendations</h2>
            <span>{items.length} items</span>
          </div>
          <div className="cards">
            {items.map((item) => (
              <RecommendationCard
                key={item.item_id}
                itemId={item.item_id}
                score={item.score}
                onWhy={() => void handleWhy(item.item_id)}
              />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}