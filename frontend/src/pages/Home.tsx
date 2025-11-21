import { useEffect, useState } from 'react';
import { Tweet } from '@/types';
import TweetCard from '@/components/tweet/TweetCard';
import TweetComposer from '@/components/tweet/TweetComposer';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { motion } from 'framer-motion';
import { tweetService } from '@/services/tweetService';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';

const Home = () => {
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [activeTab, setActiveTab] = useState('for-you');
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const { toast } = useToast();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchTweets(true);
    }
  }, [activeTab, user]);

  const fetchTweets = async (reset = false) => {
    if (!user) return;
    
    try {
      setIsLoading(true);
      const currentPage = reset ? 1 : page;
      
      const response = await tweetService.getHomeFeed(currentPage, 20);
      
      if (reset) {
        setTweets(response.results);
        setPage(2);
      } else {
        setTweets(prev => [...prev, ...response.results]);
        setPage(prev => prev + 1);
      }
      
      setHasMore(!!response.next);
    } catch (error: any) {
      console.error('Failed to fetch tweets:', error);
      toast({
        title: 'Failed to load tweets',
        description: 'Please try again later.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 border-r border-border">
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="w-full h-14 rounded-none bg-transparent border-0">
            <TabsTrigger
              value="for-you"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              For you
            </TabsTrigger>
            <TabsTrigger
              value="following"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Following
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </header>

      <TweetComposer onTweetPosted={() => fetchTweets(true)} showCommunitySelector={true} />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {isLoading && tweets.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            Loading tweets...
          </div>
        ) : tweets.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No tweets to show. Follow some users to see their tweets here!
          </div>
        ) : (
          <>
            {tweets.map((tweet) => (
              <TweetCard key={tweet.id} tweet={tweet} />
            ))}
            {hasMore && (
              <div className="p-4 text-center">
                <button
                  onClick={() => fetchTweets(false)}
                  disabled={isLoading}
                  className="text-primary hover:underline"
                >
                  {isLoading ? 'Loading...' : 'Load more tweets'}
                </button>
              </div>
            )}
          </>
        )}
      </motion.div>
    </div>
  );
};

export default Home;
