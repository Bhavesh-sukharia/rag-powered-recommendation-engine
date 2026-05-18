import { Plus } from 'lucide-react';
import { useState } from 'react';
import { useSimulatorStore } from '@/store/simulatorStore';

const AVATAR_COLORS = [
  '#EEEDFE',
  '#E1F5EE',
  '#FFF1E6',
  '#E0F2FE',
  '#F3E8FF',
];

const GENRES = [
  'Action',
  'Adventure',
  'Animation',
  'Biography',
  'Comedy',
  'Crime',
  'Drama',
  'Fantasy',
  'Horror',
  'Mystery',
  'Romance',
  'Sci-Fi',
  'Thriller',
];

function getAvatarColor(userId: number) {
  return AVATAR_COLORS[userId % AVATAR_COLORS.length];
}

function NewUserModal({
  isOpen,
  onClose,
  onSave,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, tastes: string[]) => void;
}) {
  const [name, setName] = useState('');
  const [selectedTastes, setSelectedTastes] = useState<string[]>([]);
  const [hoveredTaste, setHoveredTaste] = useState<string | null>(null);

  const handleTasteToggle = (genre: string) => {
    setSelectedTastes((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const handleSave = () => {
    if (name.trim() && selectedTastes.length > 0) {
      onSave(name, selectedTastes);
      setName('');
      setSelectedTastes([]);
    }
  };

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/50'>
      <div className='max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl border border-border bg-background p-6 shadow-lg'>
        <h2 className='mb-4 text-xl font-bold text-foreground'>Create New User</h2>

        <div className='space-y-4'>
          <label className='space-y-2'>
            <span className='text-sm font-medium text-foreground'>User Name</span>
            <input
              type='text'
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder='Enter user name'
              className='w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none transition focus:border-violet-500'
              onKeyPress={(e) => e.key === 'Enter' && handleSave()}
            />
          </label>

          <label className='space-y-2'>
            <span className='text-sm font-medium text-foreground'>Select Genres</span>
            <div className='flex flex-wrap gap-2 rounded-lg border border-border bg-background p-3'>
              {GENRES.map((genre) => {
                const isSelected = selectedTastes.includes(genre);
                const isHovered = hoveredTaste === genre;
                return (
                  <button
                    key={genre}
                    type='button'
                    onMouseEnter={() => setHoveredTaste(genre)}
                    onMouseLeave={() => setHoveredTaste(null)}
                    onClick={() => handleTasteToggle(genre)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                      isSelected
                        ? 'bg-violet-600 text-white'
                        : `border border-border bg-background text-foreground ${isHovered ? 'border-violet-500' : ''}`
                    }`}
                  >
                    {genre}
                  </button>
                );
              })}
            </div>
            {selectedTastes.length === 0 && (
              <p className='text-xs text-muted-foreground'>Select at least one genre</p>
            )}
          </label>

          <div className='flex gap-2 pt-4'>
            <button
              type='button'
              onClick={onClose}
              className='flex-1 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium text-foreground hover:bg-muted'
            >
              Cancel
            </button>
            <button
              type='button'
              onClick={handleSave}
              disabled={!name.trim() || selectedTastes.length === 0}
              className='flex-1 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50'
            >
              Save User
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function UserList() {
  const users = useSimulatorStore((state) => state.users);
  const activeUserId = useSimulatorStore((state) => state.activeUserId);
  const setActiveUser = useSimulatorStore((state) => state.setActiveUser);
  const addUser = useSimulatorStore((state) => state.addUser);
  const activeUser = users.find((user) => user.id === activeUserId) ?? users[0];
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateUser = (name: string, tastes: string[]) => {
    addUser(name, tastes);
    setIsModalOpen(false);
  };

  return (
    <div>
      <h3 className='mb-3 text-xs uppercase tracking-wider text-muted-foreground'>Select User</h3>

      <select
        value={activeUserId}
        onChange={(event) => setActiveUser(Number(event.target.value))}
        className='relative w-full appearance-none rounded-xl border border-border bg-background px-4 py-3 pr-10 text-sm font-medium text-foreground outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20'
      >
        {users.map((user) => (
          <option key={user.id} value={user.id}>
            {user.name}
          </option>
        ))}
      </select>

      <style>{`
        select {
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 0.75rem center;
          background-size: 1.25rem;
          padding-right: 2.5rem;
        }
      `}</style>

      {activeUser && (
        <div className='mt-3 flex items-center gap-2 rounded-lg px-1 py-1'>
          <div
            className='flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg font-semibold text-gray-700 dark:text-gray-900'
            style={{ background: getAvatarColor(activeUser.id) }}
          >
            {activeUser.name[0]?.toUpperCase()}
          </div>
          <div className='min-w-0 flex-1'>
            <div className='truncate text-xs font-medium'>{activeUser.name}</div>
            <div className='truncate text-xs text-muted-foreground'>
              {activeUser.tastes.join(', ')}
            </div>
          </div>
        </div>
      )}

      <button
        type='button'
        onClick={() => setIsModalOpen(true)}
        className='mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-violet-500 bg-violet-50 px-4 py-2 text-sm font-medium text-violet-700 hover:bg-violet-100 dark:bg-violet-950/30 dark:text-violet-300 dark:hover:bg-violet-950/50'
      >
        <Plus className='h-4 w-4' />
        New User
      </button>

      <NewUserModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onSave={handleCreateUser} />
    </div>
  );
}
