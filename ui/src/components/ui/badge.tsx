import React from 'react';
import { cn } from '@/libs/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {}

function Badge({ className, ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-colors',
        className
      )}
      {...props}
    />
  );
}

export { Badge };
