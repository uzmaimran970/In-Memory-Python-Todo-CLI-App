interface LoadingSkeletonProps {
  height?: string;
  width?: string;
  className?: string;
  count?: number;
}

export default function LoadingSkeleton({
  height = 'h-24',
  width = 'w-full',
  className = '',
  count = 1,
}: LoadingSkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`
            animate-pulse bg-gray-200 rounded-lg
            ${height} ${width} ${className}
          `}
          role="status"
          aria-label="Loading content"
        >
          <span className="sr-only">Loading...</span>
        </div>
      ))}
    </>
  );
}
