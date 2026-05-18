import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationControlsProps {
  page: number;
  pageCount: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export default function PaginationControls({
  page,
  pageCount,
  totalItems,
  pageSize,
  onPageChange,
}: PaginationControlsProps) {
  if (pageCount <= 1) return null;

  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalItems);

  return (
    <div className='flex items-center justify-between gap-3 rounded-xl border bg-muted/30 px-3 py-2'>
      <div className='text-xs text-muted-foreground'>
        Showing {start}-{end} of {totalItems}
      </div>

      <div className='flex items-center gap-2'>
        <button
          type='button'
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page <= 1}
          className='inline-flex items-center gap-1 rounded-lg border bg-background px-3 py-2 text-xs font-medium transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50'
        >
          <ChevronLeft className='h-3.5 w-3.5' />
          Prev
        </button>

        <div className='rounded-lg bg-background px-3 py-2 text-xs font-medium'>
          Page {page} of {pageCount}
        </div>

        <button
          type='button'
          onClick={() => onPageChange(Math.min(pageCount, page + 1))}
          disabled={page >= pageCount}
          className='inline-flex items-center gap-1 rounded-lg border bg-background px-3 py-2 text-xs font-medium transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50'
        >
          Next
          <ChevronRight className='h-3.5 w-3.5' />
        </button>
      </div>
    </div>
  );
}