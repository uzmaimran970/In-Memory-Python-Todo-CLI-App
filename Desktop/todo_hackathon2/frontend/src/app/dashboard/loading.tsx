import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

export default function DashboardLoading() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Skeleton */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <LoadingSkeleton height="h-8" width="w-8" />
              <LoadingSkeleton height="h-6" width="w-24" />
            </div>
            <LoadingSkeleton height="h-9" width="w-20" />
          </div>
        </div>
      </div>

      {/* Main Content Skeleton */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Title Skeleton */}
        <LoadingSkeleton height="h-10" width="w-48" className="mb-2" />

        {/* Statistics Skeleton */}
        <LoadingSkeleton height="h-5" width="w-32" className="mb-6" />

        {/* Filters Skeleton */}
        <div className="flex items-center gap-2 mb-6">
          <LoadingSkeleton height="h-10" width="w-20" />
          <LoadingSkeleton height="h-10" width="w-20" />
          <LoadingSkeleton height="h-10" width="w-28" />
        </div>

        {/* Task Cards Skeleton */}
        <div className="space-y-3">
          <LoadingSkeleton count={5} height="h-24" />
        </div>
      </main>
    </div>
  );
}
