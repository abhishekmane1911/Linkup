// components/chat/Skeletons.tsx

export const ConversationSkeleton = () => (
  <div className="p-4">
    <div className="flex items-center gap-3 animate-pulse">
      <div className="w-12 h-12 bg-muted rounded-full"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-muted rounded w-3/4"></div>
        <div className="h-3 bg-muted rounded w-1/2"></div>
      </div>
    </div>
  </div>
);

export const MessageSkeleton = () => (
  <div className="p-4 space-y-4">
    {[...Array(3)].map((_, i) => (
      <div key={i} className={`flex items-start gap-2.5 ${i % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
        <div className={`flex flex-col w-full max-w-[320px] leading-1.5 p-4 border-gray-200 rounded-e-xl rounded-es-xl ${i % 2 === 0 ? 'bg-muted' : 'bg-primary/20'}`}>
          <div className="h-4 bg-muted-foreground/20 rounded w-3/4 mb-2 animate-pulse"></div>
          <div className="h-3 bg-muted-foreground/20 rounded w-1/2 animate-pulse"></div>
        </div>
      </div>
    ))}
  </div>
);