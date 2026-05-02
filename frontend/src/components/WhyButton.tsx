type WhyButtonProps = {
  onClick: () => void;
};


export default function WhyButton({ onClick }: WhyButtonProps) {
  return (
    <button className="badge" type="button" onClick={onClick}>
      Why this?
    </button>
  );
}