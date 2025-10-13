// components/chat/ConversationItem.tsx

import { motion } from 'framer-motion';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils'; // Assuming you have a cn utility for classnames

// Define types for clarity
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

interface ConversationItemProps {
  conversation: Conversation;
  isSelected: boolean;
  onSelect: () => void;
}

const getInitials = (name: string, fallback: string) => {
  return name?.charAt(0)?.toUpperCase() || fallback.charAt(0)?.toUpperCase() || 'U';
};

export const ConversationItem = ({ conversation, isSelected, onSelect }: ConversationItemProps) => {
  const otherParticipant = conversation.other_participant;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onSelect}
      className={cn(
        'p-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors',
        isSelected && 'bg-muted'
      )}
    >
      <div className="flex gap-3">
        <Avatar>
          <AvatarImage src={otherParticipant.profile_image_url} />
          <AvatarFallback>{getInitials(otherParticipant.full_name, otherParticipant.username)}</AvatarFallback>
        </Avatar>

        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start">
            <p className="font-bold truncate">{otherParticipant.full_name}</p>
            {conversation.last_message && (
              <span className="text-xs text-muted-foreground flex-shrink-0 ml-2">
                {formatDistanceToNow(new Date(conversation.last_message.sent_at), { addSuffix: false })}
              </span>
            )}
          </div>
          <div className="flex items-center justify-between mt-1">
            <p className="text-sm text-muted-foreground truncate flex-1">
              {conversation.last_message?.content || 'No messages yet'}
            </p>
            {conversation.unread_count > 0 && (
              <span className="bg-primary text-primary-foreground text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center ml-2">
                {conversation.unread_count}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};