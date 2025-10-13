// components/chat/ChatPlaceholder.tsx

import { MessageSquareText } from 'lucide-react';

export const ChatPlaceholder = () => (
  <div className="hidden md:flex flex-1 flex-col items-center justify-center text-muted-foreground">
    <MessageSquareText size={48} className="mb-4" />
    <h3 className="text-xl font-semibold">Select a conversation</h3>
    <p>Choose from your existing conversations to start chatting.</p>
  </div>
);