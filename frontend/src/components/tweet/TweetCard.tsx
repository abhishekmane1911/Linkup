import { useState } from 'react';
import { Heart, Repeat2, MessageCircle, Bookmark, Share, MoreHorizontal } from 'lucide-react';
import { Tweet } from '@/types';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { tweetService } from '@/services/tweetService';
import { useToast } from '@/hooks/use-toast';

interface TweetCardProps {
  tweet: Tweet;
}

const TweetCard = ({ tweet }: TweetCardProps) => {
  const [liked, setLiked] = useState(tweet.is_liked);
  const [retweeted, setRetweeted] = useState(tweet.is_retweeted);
  const [bookmarked, setBookmarked] = useState(tweet.is_bookmarked);
  const [likesCount, setLikesCount] = useState(tweet.likes_count);
  const [retweetsCount, setRetweetsCount] = useState(tweet.retweets_count);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleLike = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await tweetService.likeTweet(tweet.id);
      setLiked(response.liked);
      setLikesCount(response.likes_count);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update like status',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetweet = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await tweetService.retweetTweet(tweet.id);
      setRetweeted(response.retweeted);
      setRetweetsCount(response.retweets_count);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update retweet status',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBookmark = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await tweetService.bookmarkTweet(tweet.id);
      setBookmarked(response.bookmarked);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update bookmark status',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-border p-4 hover:bg-muted/50 transition-colors cursor-pointer"
    >
      <div className="flex gap-3">
        <Avatar className="w-12 h-12">
          <AvatarImage src={tweet.author.profile_image_url} />
          <AvatarFallback>{tweet.author.first_name?.[0] || tweet.author.username?.[0] || 'U'}</AvatarFallback>
        </Avatar>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-bold hover:underline">{tweet.author.first_name}</span>
            <span className="text-muted-foreground">@{tweet.author.username}</span>
            <span className="text-muted-foreground">·</span>
            <span className="text-muted-foreground text-sm">
              {formatDistanceToNow(new Date(tweet.created_at), { addSuffix: true })}
            </span>
            <Button variant="ghost" size="icon" className="ml-auto h-8 w-8">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </div>

          <p className="mb-3 whitespace-pre-wrap break-words">{tweet.content}</p>

          {tweet.media && tweet.media.length > 0 && (
            <div className="mb-3 rounded-2xl overflow-hidden border border-border">
              <img
                src={tweet.media[0].file_url}
                alt={tweet.media[0].alt_text || "Tweet media"}
                className="w-full object-cover max-h-96"
              />
            </div>
          )}

          <div className="flex items-center justify-between max-w-md">
            <Button variant="ghost" size="sm" className="gap-2 hover:text-primary">
              <MessageCircle className="w-4 h-4" />
              <span className="text-sm">{tweet.reply_count}</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className={`gap-2 ${retweeted ? 'text-green-500' : 'hover:text-green-500'}`}
              onClick={(e) => {
                e.stopPropagation();
                handleRetweet();
              }}
            >
              <Repeat2 className="w-4 h-4" />
              <span className="text-sm">{retweetsCount}</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className={`gap-2 ${liked ? 'text-pink-500' : 'hover:text-pink-500'}`}
              onClick={(e) => {
                e.stopPropagation();
                handleLike();
              }}
            >
              <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
              <span className="text-sm">{likesCount}</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className={`${bookmarked ? 'text-primary' : 'hover:text-primary'}`}
              onClick={(e) => {
                e.stopPropagation();
                handleBookmark();
              }}
            >
              <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-current' : ''}`} />
            </Button>

            <Button variant="ghost" size="sm" className="hover:text-primary">
              <Share className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </motion.article>
  );
};

export default TweetCard;
