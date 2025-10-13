// components/chat/MessageBubble.tsx

import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { Check, CheckCheck } from 'lucide-react';
import { cn } from '@/lib/utils';

// Define DirectMessage type here or import from types
interface DirectMessage {
  message_id: number;
  content: string;
  sent_at: string;
  is_read: boolean;
}

interface MessageBubbleProps {
  message: DirectMessage;
  isCurrentUser: boolean;
}

export const MessageBubble = ({ message, isCurrentUser }: MessageBubbleProps) => {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, y: 10 }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
      className={cn('flex items-end gap-2', isCurrentUser ? 'justify-end' : 'justify-start')}
    >
      <div
        className={cn(
          'max-w-md w-fit px-4 py-2.5 rounded-2xl',
          isCurrentUser
            ? 'bg-primary text-primary-foreground rounded-br-none'
            : 'bg-muted rounded-bl-none'
        )}
      >
        <p className="break-words whitespace-pre-wrap">{message.content}</p>
        <div className="flex items-center gap-2 mt-1.5 text-xs opacity-70 float-right">
          <span>{formatDistanceToNow(new Date(message.sent_at), { addSuffix: true })}</span>
          {isCurrentUser && (
            <span>
              {message.is_read ? <CheckCheck size={14} /> : <Check size={14} />}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
};