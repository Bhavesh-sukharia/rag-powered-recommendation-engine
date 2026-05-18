import { useSimulatorStore } from '@/store/simulatorStore';

export default function EventLog() {
  const events = useSimulatorStore((state) => state.events);

  return (
    <div className='space-y-3'>
      {events.map((event, index) => (
        <div key={index} className='flex items-center gap-4 rounded-xl border p-4'>
          <span className='rounded-full bg-violet-100 px-2 py-1 text-xs text-violet-700'>
            {event.type}
          </span>

          <div className='flex-1 text-sm'>{event.text}</div>
          <div className='text-xs text-muted-foreground'>{event.time}</div>
        </div>
      ))}
    </div>
  );
}
