import { useState, useEffect, useRef } from 'react';
import { Conversation, DirectMessage } from '@/types';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send } from 'lucide-react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { messagingService } from '@/services/messagingService';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

const Messages = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<any | null>(null);
  const [messages, setMessages] = useState<DirectMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user) {
      fetchConversations();
    }
  }, [user]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Helper function to safely format dates
  const formatSafeDate = (dateString: string | undefined) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) ? '' : formatDistanceToNow(date, { addSuffix: false });
    } catch {
      return '';
    }
  };

  // Helper function to get the other participant in a conversation
  const getOtherParticipant = (conversation: any) => {
    // The backend returns other_participant directly, not in a participants array
    if (conversation.other_participant) {
      return {
        id: conversation.other_participant.id,
        username: conversation.other_participant.username,
        first_name: conversation.other_participant.first_name,
        last_name: conversation.other_participant.last_name,
        full_name: `${conversation.other_participant.first_name} ${conversation.other_participant.last_name}`.trim(),
        profile_image_url: conversation.other_participant.profile_image,
        is_verified: false
      };
    }
    
    // Fallback if no other_participant
    return {
      id: 0,
      username: 'unknown',
      first_name: 'Unknown',
      last_name: 'User',
      full_name: 'Unknown User',
      profile_image_url: undefined,
      is_verified: false
    };
  };

  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      const response = await messagingService.getConversations();
      
      const transformedConversations: any[] = response.results.map((conv) => ({
        ...conv,
        conversation_id: conv.id, // Use id as conversation_id
        participants: conv.other_participant ? [conv.other_participant] : [], // Convert other_participant to participants array
        last_message: conv.last_message ? {
          ...conv.last_message,
          conversation_id: conv.id,
          sent_at: conv.last_message.created_at // Map created_at to sent_at
        } : undefined
      }));
      
      setConversations(transformedConversations);
    } catch (error: any) {
      console.error('Failed to fetch conversations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load conversations',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const selectConversation = async (conversation: any) => {
    setSelectedConversation(conversation);
    
    try {
      setIsLoadingMessages(true);
      const response = await messagingService.getMessages(conversation.conversation_id);
      
      const transformedMessages: DirectMessage[] = response.results.map(msg => ({
        ...msg,
        conversation_id: msg.conversation_id,
        sent_at: msg.created_at // Map created_at to sent_at
      }));
      
      setMessages(transformedMessages);
      
      await messagingService.markMessagesAsRead(conversation.conversation_id);
    } catch (error: any) {
      console.error('Failed to fetch messages:', error);
      toast({
        title: 'Error',
        description: 'Failed to load messages',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation || !user) return;

    try {
      setIsSending(true);
      const messageResponse = await messagingService.sendMessage(selectedConversation.conversation_id, {
        content: newMessage.trim()
      });
      
      const message: DirectMessage = {
        ...messageResponse,
        conversation_id: messageResponse.conversation_id,
        sent_at: messageResponse.created_at // Map created_at to sent_at
      };
      
      setMessages(prev => [...prev, message]);
      setNewMessage('');
      
      // Update the conversation's last message
      setConversations(prev => 
        prev.map(conv => 
          conv.conversation_id === selectedConversation.conversation_id
            ? { ...conv, last_message: message, last_message_at: message.sent_at }
            : conv
        )
      );
    } catch (error: any) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        variant: 'destructive',
      });
    } finally {
      setIsSending(false);
    }
  };

  if (!user) {
    return <div className="flex-1 p-8">Loading user...</div>;
  }

  return (
    <div className="flex-1 border-r border-border flex h-screen">
      {/* Conversations List */}
      <div className="w-80 border-r border-border flex flex-col">
        <header className="p-4 border-b border-border">
          <h2 className="text-xl font-bold">Messages</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Start conversations by visiting user profiles
          </p>
        </header>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-muted-foreground">
              Loading conversations...
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <div className="mb-4">
                <Send className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                <h3 className="font-semibold mb-2">No conversations yet</h3>
                <p className="text-sm">
                  Visit user profiles and click the message icon to start chatting with people you follow each other.
                </p>
              </div>
            </div>
          ) : (
            conversations.map((conversation) => {
              const otherParticipant = getOtherParticipant(conversation);
              return (
                <motion.div
                  key={conversation.conversation_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => selectConversation(conversation)}
                  className={`p-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors ${
                    selectedConversation?.conversation_id === conversation.conversation_id
                      ? 'bg-muted'
                      : ''
                  }`}
                >
                  <div className="flex gap-3">
                    <Avatar>
                      <AvatarImage src={otherParticipant.profile_image_url} />
                      <AvatarFallback>
                        {otherParticipant.full_name?.[0] || otherParticipant.username?.[0] || 'U'}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-start">
                        <p className="font-bold">{otherParticipant.full_name}</p>
                        <span className="text-xs text-muted-foreground">
                          {formatSafeDate(conversation.last_message?.sent_at)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground truncate flex-1">
                          {conversation.last_message?.content}
                        </p>
                        {conversation.unread_count > 0 && (
                          <span className="bg-primary text-primary-foreground text-xs rounded-full px-2 py-1 ml-2">
                            {conversation.unread_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </div>

      {/* Messages Area */}
      {selectedConversation ? (
        <div className="flex-1 flex flex-col">
          <header className="p-4 border-b border-border flex items-center gap-3">
            {(() => {
              const otherParticipant = getOtherParticipant(selectedConversation);
              return (
                <>
                  <Avatar>
                    <AvatarImage src={otherParticipant.profile_image_url} />
                    <AvatarFallback>
                      {otherParticipant.full_name?.[0] || otherParticipant.username?.[0] || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-bold">{otherParticipant.full_name}</p>
                    <p className="text-sm text-muted-foreground">@{otherParticipant.username}</p>
                  </div>
                </>
              );
            })()}
          </header>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {isLoadingMessages ? (
              <div className="text-center text-muted-foreground">
                Loading messages...
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center text-muted-foreground">
                No messages yet. Start the conversation!
              </div>
            ) : (
              messages.map((message) => (
                <motion.div
                  key={message.message_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.sender_user_id === user?.id ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-md px-4 py-2 rounded-2xl ${
                      message.sender_user_id === user?.id
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="break-words">{message.content}</p>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs opacity-70">
                        {formatSafeDate(message.sent_at)}
                      </p>
                      {message.sender_user_id === user?.id && (
                        <span className="text-xs opacity-70">
                          {message.is_read ? '✓✓' : '✓'}
                        </span>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-border">
            <div className="flex gap-2">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Start a new message"
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              />
              <Button onClick={sendMessage} size="icon" disabled={isSending || !newMessage.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-muted-foreground">
          <p>Select a conversation to start messaging</p>
        </div>
      )}
    </div>
  );
};

export default Messages;