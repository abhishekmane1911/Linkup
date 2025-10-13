// components/chat/ConversationList.tsx

import { Send } from 'lucide-react';
import { ConversationItem } from './ConversationItem';
import { ConversationSkeleton } from './Skeletons';

// Match types with ConversationItem
interface Participant {
  profile_image_url: string;
  full_name: string;
  username: string;
}
interface Conversation {
  conversation_id: number;
  last_message?: { content: string; sent_at: string };
  unread_count: number;
  other_participant: Participant;
}

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversationId: number | null;
  onSelectConversation: (conversation: Conversation) => void;
  isLoading: boolean;
}

export const ConversationList = ({
  conversations,
  selectedConversationId,
  onSelectConversation,
  isLoading,
}: ConversationListProps) => {
  return (
    <div className="w-full md:w-80 border-r border-border flex flex-col h-screen">
      <header className="p-4 border-b border-border">
        <h2 className="text-xl font-bold">Messages</h2>
        <p className="text-sm text-muted-foreground mt-1">Your recent conversations.</p>
      </header>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <>
            <ConversationSkeleton />
            <ConversationSkeleton />
            <ConversationSkeleton />
          </>
        ) : conversations.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground h-full flex flex-col justify-center items-center">
            <Send className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="font-semibold mb-2">No conversations yet</h3>
            <p className="text-sm">Visit a user's profile to start chatting.</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <ConversationItem
              key={conv.conversation_id}
              conversation={conv}
              isSelected={selectedConversationId === conv.conversation_id}
              onSelect={() => onSelectConversation(conv)}
            />
          ))
        )}
      </div>
    </div>
  );
};