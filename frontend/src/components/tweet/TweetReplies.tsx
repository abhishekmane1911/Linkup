import { useState, useEffect } from 'react';
import { Tweet } from '@/types';
import { tweetService } from '@/services/tweetService';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2 } from 'lucide-react';
import TweetCard from './TweetCard';
import { motion, AnimatePresence } from 'framer-motion';

interface TweetRepliesProps {
  tweetId: number;
  initialReplyCount: number;
  nestingLevel?: number; // Track nesting level to pass to child TweetCards
}

const TweetReplies = ({ tweetId, initialReplyCount, nestingLevel = 0 }: TweetRepliesProps) => {
  const [replies, setReplies] = useState<Tweet[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [hasMore, setHasMore] = useState(false);
  const [page, setPage] = useState(1);
  const { toast } = useToast();

  useEffect(() => {
    fetchReplies();
  }, [tweetId]);

  const fetchReplies = async (pageNum = 1) => {
    try {
      setIsLoading(true);
      const response = await tweetService.getTweetReplies(tweetId, pageNum, 10);
      
      if (pageNum === 1) {
        setReplies(response.results);
      } else {
        setReplies(prev => [...prev, ...response.results]);
      }
      
      setHasMore(!!response.next);
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to fetch replies:', error);
      toast({
        title: 'Error',
        description: 'Failed to load replies',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReply = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!replyContent.trim()) {
      toast({
        title: 'Error',
        description: 'Reply cannot be empty',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsSubmitting(true);
      const newReply = await tweetService.createReply(tweetId, replyContent.trim());
      
      setReplies(prev => [newReply, ...prev]);
      setReplyContent('');
      
      toast({
        title: 'Success',
        description: 'Reply posted successfully',
      });
    } catch (error: any) {
      console.error('Failed to post reply:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to post reply',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadMore = () => {
    if (!isLoading && hasMore) {
      fetchReplies(page + 1);
    }
  };

  return (
    <div className="border-t border-border">
      {/* Reply Input */}
      <div className="p-4 bg-muted/30">
        <form onSubmit={handleSubmitReply} className="space-y-3">
          <Textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder="Post your reply..."
            className="min-h-[80px] resize-none"
            disabled={isSubmitting}
          />
          <div className="flex justify-end">
            <Button
              type="submit"
              size="sm"
              disabled={isSubmitting || !replyContent.trim()}
              className="gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Posting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Reply
                </>
              )}
            </Button>
          </div>
        </form>
      </div>

      {/* Replies List */}
      <div className="divide-y divide-border">
        {isLoading && page === 1 ? (
          <div className="p-8 text-center">
            <Loader2 className="w-6 h-6 animate-spin mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground mt-2">Loading replies...</p>
          </div>
        ) : replies.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <p>No replies yet. Be the first to reply!</p>
          </div>
        ) : (
          <>
            <AnimatePresence mode="popLayout">
              {replies.map((reply) => (
                <motion.div
                  key={reply.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  <TweetCard tweet={reply} nestingLevel={nestingLevel + 1} />
                </motion.div>
              ))}
            </AnimatePresence>

            {hasMore && (
              <div className="p-4 text-center">
                <Button
                  variant="ghost"
                  onClick={loadMore}
                  disabled={isLoading}
                  className="gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading more...
                    </>
                  ) : (
                    'Load more replies'
                  )}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TweetReplies;
