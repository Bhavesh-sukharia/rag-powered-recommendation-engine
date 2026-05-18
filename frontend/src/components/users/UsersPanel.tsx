import { useEffect, useRef, useState } from 'react';

import { apiClient } from '@/lib/api';
import { useSimulatorStore } from '@/store/simulatorStore';
import { User } from '@/types/user';

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

const AVATAR_COLORS = [
  '#EEEDFE',
  '#E1F5EE',
  '#FFF1E6',
  '#E0F2FE',
  '#F3E8FF',
];

function getAvatarColor(userId: number) {
  return AVATAR_COLORS[userId % AVATAR_COLORS.length];
}

function UserCard({ user }: { user: User }) {
  const activeUserId = useSimulatorStore((state) => state.activeUserId);
  const updateUser = useSimulatorStore((state) => state.updateUser);
  const loadUsers = useSimulatorStore((state) => state.loadUsers);
  const setActiveUser = useSimulatorStore((state) => state.setActiveUser);
  const isActive = activeUserId === user.id;
  const [draft, setDraft] = useState(user);
  const [hoveredTaste, setHoveredTaste] = useState<string | null>(null);
  const usersList = useSimulatorStore((s) => s.users);

  useEffect(() => {
    setDraft(user);
  }, [user]);

  const handleTasteChange = (genre: string) => {
    setDraft((current) => {
      const newTastes = current.tastes.includes(genre)
        ? current.tastes.filter((t) => t !== genre)
        : [...current.tastes, genre];
      return { ...current, tastes: newTastes };
    });
  };

  return (
    <div
      className={`rounded-2xl border bg-background p-5 transition ${
        isActive ? 'border-violet-500 shadow-sm' : 'border-border'
      }`}
    >
      <div className='mb-4 flex items-start gap-4'>
        <div
          className='flex h-12 w-12 items-center justify-center rounded-full text-lg font-semibold text-gray-700 dark:text-gray-900'
          style={{ background: getAvatarColor(user.id) }}
        >
          {user.name[0]?.toUpperCase()}
        </div>

        <div className='flex-1'>
          <div className='flex items-center gap-2'>
            <h3 className='text-lg font-semibold'>{user.name}</h3>
            {isActive && (
              <span className='rounded-full bg-violet-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-violet-700 dark:bg-violet-950 dark:text-violet-200'>
                Active
              </span>
            )}
          </div>
          <p className='text-xs text-muted-foreground'>User ID: {user.id}</p>
        </div>
      </div>

      <div className='space-y-3'>
        <label className='space-y-1 text-sm'>
          <span className='text-xs uppercase tracking-wider text-muted-foreground'>Name</span>
          <input
            value={draft.name}
            onChange={(event) => setDraft((current) => ({ ...current, name: event.target.value }))}
            className='w-full rounded-lg border border-border bg-background px-3 py-2 outline-none transition focus:border-violet-500'
          />
        </label>

        <label className='space-y-2 text-sm'>
          <span className='text-xs uppercase tracking-wider text-muted-foreground'>Genres</span>
          <div className='flex flex-wrap gap-2'>
            {GENRES.map((genre) => {
              const isSelected = draft.tastes.includes(genre);
              const isHovered = hoveredTaste === genre;
              return (
                <button
                  key={genre}
                  type='button'
                  onMouseEnter={() => setHoveredTaste(genre)}
                  onMouseLeave={() => setHoveredTaste(null)}
                  onClick={() => handleTasteChange(genre)}
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
        </label>
      </div>

      <div className='mt-4 flex gap-2'>
        <button
          type='button'
          onClick={() => updateUser(user.id, draft)}
          className='flex-1 rounded-lg bg-violet-600 px-4 py-2 text-sm text-white hover:bg-violet-700'
        >
          Update User
        </button>
        {user.id !== 1 && (
          <button
            type='button'
            onClick={async () => {
              if (!confirm(`Delete user ${user.name}? This action cannot be undone.`)) return;
              try {
                // call backend using apiId if available
                const backendId = (user as any).apiId ?? String(user.id);
                await apiClient.delete(`/api/users/${backendId}`);
                // refresh users and select default user (1)
                await loadUsers();
                setActiveUser(1);
              } catch (e) {
                // eslint-disable-next-line no-console
                console.error('Failed to delete user', e);
                alert('Failed to delete user');
              }
            }}
            className='rounded-lg bg-red-500 px-4 py-2 text-sm text-white hover:bg-red-600'
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

export default function UsersPanel() {
  const users = useSimulatorStore((state) => state.users);
  const loadMoreUsers = useSimulatorStore((state) => state.loadMoreUsers);
  const isLoadingMoreUsers = useSimulatorStore((state) => state.isLoadingMoreUsers);
  const totalUserCount = useSimulatorStore((state) => state.totalUserCount);
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          void loadMoreUsers();
        }
      },
      { threshold: 0.1 }
    );

    if (sentinelRef.current) observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [loadMoreUsers]);

  return (
    <div className='space-y-4'>
      <div className='mb-2'>
        <h2 className='text-2xl font-bold text-foreground'>Users</h2>
        <p className='text-sm text-muted-foreground'>
          Showing {users.length} of {totalUserCount} users. Edit user details and save changes instantly.
        </p>
      </div>

      <div className='grid gap-4 xl:grid-cols-2'>
        {users.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>
      <div ref={sentinelRef} className='flex justify-center py-6'>
        {isLoadingMoreUsers && (
          <div className='flex items-center gap-2'>
            <svg className='h-5 w-5 animate-spin text-violet-600' viewBox='0 0 24 24' fill='none'>
              <circle className='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' strokeWidth='4'></circle>
              <path className='opacity-75' fill='currentColor' d='M4 12a8 8 0 018-8v8z'></path>
            </svg>
            <span className='text-sm text-muted-foreground'>Loading more users...</span>
          </div>
        )}
      </div>
    </div>
  );
}
