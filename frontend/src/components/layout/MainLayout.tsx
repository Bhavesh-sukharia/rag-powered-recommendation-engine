import { ReactNode } from 'react';

import Sidebar from './Sidebar';
import Topbar from './Topbar';

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className='flex h-screen overflow-hidden bg-background text-foreground'>
      <Sidebar />

      <div className='flex flex-1 flex-col overflow-hidden'>
        <Topbar />

        <div className='flex-1 overflow-y-auto p-6'>{children}</div>
      </div>
    </div>
  );
}
