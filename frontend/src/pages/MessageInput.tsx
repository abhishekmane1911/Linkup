// components/chat/MessageInput.tsx

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (content: string) => Promise<void>;
  isSending: boolean;
}

export const MessageInput = ({ onSendMessage, isSending }: MessageInputProps) => {
  const [newMessage, setNewMessage] = useState('');

  const handleSend = async () => {
    if (!newMessage.trim()) return;
    await onSendMessage(newMessage.trim());
    setNewMessage('');
  };

  return (
    <div className="p-4 border-t border-border bg-background">
      <div className="flex items-center gap-2">
        <Input
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Start a new message"
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={isSending}
          className="flex-1"
        />
        <Button onClick={handleSend} size="icon" disabled={isSending || !newMessage.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};