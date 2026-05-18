export interface EventLogItem {
  type: 'rate' | 'review' | 'rec' | 'user';
  text: string;
  time: string;
}
