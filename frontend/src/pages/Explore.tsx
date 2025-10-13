import { useState, useEffect } from 'react';
import { Search, User } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { tweetService } from '@/services/tweetService';
import { userService } from '@/services/userService';
import { useToast } from '@/hooks/use-toast';
import UserCard from '@/components/user/UserCard';

interface UserProfile {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  profile_image_url?: string;
  is_verified: boolean;
  followers_count: number;
  following_count: number;
  is_following: boolean;
}

const Explore = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [trendingTopics, setTrendingTopics] = useState<{ hashtag: string; count: number }[]>([]);
  const [searchResults, setSearchResults] = useState<UserProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchTrendingHashtags();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const debounceTimer = setTimeout(() => {
        searchUsers();
      }, 300);
      return () => clearTimeout(debounceTimer);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const fetchTrendingHashtags = async () => {
    try {
      setIsLoading(true);
      console.log('Fetching trending hashtags...');
      const hashtags = await tweetService.getTrendingHashtags();
      console.log('Received hashtags:', hashtags);
      // Ensure we always set an array
      setTrendingTopics(Array.isArray(hashtags) ? hashtags : []);
      console.log('Set trending topics:', Array.isArray(hashtags) ? hashtags : []);
    } catch (error: any) {
      console.error('Failed to fetch trending hashtags:', error);
      // Always set empty array on error
      setTrendingTopics([]);
    } finally {
      setIsLoading(false);
    }
  };

  const searchUsers = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setIsSearching(true);
      const response = await userService.searchUsers(searchQuery.trim());
      setSearchResults(response.results);
    } catch (error: any) {
      console.error('Failed to search users:', error);
      toast({
        title: 'Search failed',
        description: 'Failed to search users. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleUserUpdate = (updatedUser: UserProfile) => {
    setSearchResults(prev => 
      prev.map(user => 
        user.id === updatedUser.id ? updatedUser : user
      )
    );
  };

  return (
    <div className="flex-1 border-r border-border">
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Linkup"
            className="pl-11"
          />
        </div>
      </header>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-4 space-y-4"
      >
        {/* Search Results */}
        {searchQuery.trim() && (
          <Card>
            <CardContent className="p-4">
              <h2 className="text-xl font-bold mb-4">Search Results</h2>
              <div className="space-y-4">
                {isSearching ? (
                  <div className="text-center text-muted-foreground py-8">
                    Searching users...
                  </div>
                ) : searchResults.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    <User className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                    <h3 className="font-semibold mb-2">No users found</h3>
                    <p className="text-sm">Try searching with a different term.</p>
                  </div>
                ) : (
                  searchResults.map((user) => (
                    <UserCard
                      key={user.id}
                      user={user}
                      onUserUpdate={handleUserUpdate}
                    />
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Trending Topics */}
        <Card>
          <CardContent className="p-4">
            <h2 className="text-xl font-bold mb-4">Trending Now</h2>
            <div className="space-y-4">
              {isLoading ? (
                <div className="text-center text-muted-foreground py-8">
                  Loading trending topics...
                </div>
              ) : trendingTopics.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="font-semibold mb-2">No trending topics yet</h3>
                  <p className="text-sm">Start using hashtags in your tweets to see trends!</p>
                </div>
              ) : (
                Array.isArray(trendingTopics) && trendingTopics.map((trend, index) => (
                  <motion.div
                    key={trend.hashtag}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start justify-between p-3 rounded-lg hover:bg-muted transition-colors cursor-pointer"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="secondary">{index + 1}</Badge>
                        <span className="text-sm text-muted-foreground">Trending</span>
                      </div>
                      <p className="font-bold text-lg">#{trend.hashtag}</p>
                      <p className="text-sm text-muted-foreground">
                        {trend.count} {trend.count === 1 ? 'tweet' : 'tweets'}
                      </p>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Explore;
