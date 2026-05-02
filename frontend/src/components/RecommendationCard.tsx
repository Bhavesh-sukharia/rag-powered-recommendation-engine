import WhyButton from './WhyButton';


type RecommendationCardProps = {
  itemId: string;
  score: number;
  sentiment?: string;
  onWhy: () => void;
};


export default function RecommendationCard({ itemId, score, sentiment = 'positive', onWhy }: RecommendationCardProps) {
  return (
    <article className="card">
      <h3>{itemId}</h3>
      <p>Rank score: {score.toFixed(3)}</p>
      <div className="badges">
        <span className="badge">Sentiment: {sentiment}</span>
        <WhyButton onClick={onWhy} />
      </div>
    </article>
  );
}