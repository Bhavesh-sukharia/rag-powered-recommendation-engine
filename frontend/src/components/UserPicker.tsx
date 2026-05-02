type UserPickerProps = {
  value: string;
  onChange: (value: string) => void;
};


export default function UserPicker({ value, onChange }: UserPickerProps) {
  return (
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      <option value="user-001">user-001</option>
      <option value="user-002">user-002</option>
      <option value="user-003">user-003</option>
    </select>
  );
}