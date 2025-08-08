import React from 'react';

type SkeletonProps = {
  className?: string;
};

export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => (
  <div className={`animate-pulse bg-neutral-800/60 rounded-xl ${className}`} />
);

export const SkeletonText: React.FC<SkeletonProps> = ({ className = '' }) => (
  <div className={`animate-pulse bg-neutral-800/60 rounded ${className}`} />
);

export const SkeletonCircle: React.FC<SkeletonProps> = ({ className = '' }) => (
  <div className={`animate-pulse bg-neutral-800/60 rounded-full ${className}`} />
);

export default Skeleton;

 