import { Film, Sparkles, Users } from 'lucide-react';

import { useSimulatorStore } from '@/store/simulatorStore';
import ThemeToggle from './ThemeToggle';

const tabs = [
  { id: 'recommendations', label: 'Recommendations', icon: Sparkles },
  { id: 'catalog', label: 'Rate Movies', icon: Film },
  { id: 'users', label: 'Users', icon: Users },
] as const;

export default function Topbar() {
  const activeTab = useSimulatorStore((state) => state.activeTab);
  const setActiveTab = useSimulatorStore((state) => state.setActiveTab);

  return (
    <div className='flex items-center gap-2 border-b bg-background px-4 py-3'>
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            type='button'
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm transition ${
              isActive
                ? 'bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-200'
                : 'hover:bg-muted'
            }`}
          >
            <Icon className='h-4 w-4' />
            {tab.label}
          </button>
        );
      })}

      <div className='ml-auto'>
        <ThemeToggle />
      </div>
    </div>
  );
}
