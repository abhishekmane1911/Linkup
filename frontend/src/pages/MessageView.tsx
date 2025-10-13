// components/chat/MessageView.tsx

import { useEffect, useRef } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { MessageSkeleton } from './Skeletons';

// Types should be imported or defined consistently
interface Participant {
  profile_image_url: string;
  full_name: string;
  username: string;
}
interface Conversation {
  conversation_id: number;
  other_participant: Participant;
}
interface DirectMessage {
  message_id: number;
  sender_user_id: number;
  content: string;
  sent_at: string;
  is_read: boolean;
}
interface User {
  id: number;
}

interface MessageViewProps {
  conversation: Conversation;
  messages: DirectMessage[];
  currentUser: User;
  onSendMessage: (content: string) => Promise<void>;
  isLoadingMessages: boolean;
  isSending: boolean;
}

const getInitials = (name: string, fallback: string) => {
    return name?.charAt(0)?.toUpperCase() || fallback.charAt(0)?.toUpperCase() || 'U';
};

export const MessageView = ({
  conversation,
  messages,
  currentUser,
  onSendMessage,
  isLoadingMessages,
  isSending,
}: MessageViewProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const otherParticipant = conversation.other_participant;

  return (
    <div className="flex-1 flex flex-col h-screen">
      {/* Header */}
      <header className="p-4 border-b border-border flex items-center gap-3">
        <Avatar>
          <AvatarImage src={otherParticipant.profile_image_url} />
          <AvatarFallback>{getInitials(otherParticipant.full_name, otherParticipant.username)}</AvatarFallback>
        </Avatar>
        <div>
          <p className="font-bold">{otherParticipant.full_name}</p>
          <p className="text-sm text-muted-foreground">@{otherParticipant.username}</p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoadingMessages ? (
          <MessageSkeleton />
        ) : messages.length === 0 ? (
          <div className="text-center text-muted-foreground h-full flex items-center justify-center">
            No messages yet. Start the conversation!
          </div>
        ) : (
          <AnimatePresence>
            {messages.map((message) => (
              <MessageBubble
                key={message.message_id}
                message={message}
                isCurrentUser={message.sender_user_id === currentUser.id}
              />
            ))}
          </AnimatePresence>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput onSendMessage={onSendMessage} isSending={isSending} />
    </div>
  );
};