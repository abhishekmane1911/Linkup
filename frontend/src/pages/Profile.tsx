import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Calendar, MessageCircle } from 'lucide-react';
import { User, Tweet } from '@/types';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import TweetCard from '@/components/tweet/TweetCard';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { userService } from '@/services/userService';
import { tweetService } from '@/services/tweetService';
import { messagingService } from '@/services/messagingService';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

const Profile = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [isFollowedBy, setIsFollowedBy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingTweets, setIsLoadingTweets] = useState(true);
  const [isStartingChat, setIsStartingChat] = useState(false);
  const [isCheckingMutualFollow, setIsCheckingMutualFollow] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (username) {
      fetchUserProfile();
    } else if (currentUser) {
      // If no username in URL, show current user's profile
      setUser(currentUser);
      fetchUserTweets(currentUser.id);
    }
  }, [username, currentUser]);

  // Fetch tweets when user data is available
  useEffect(() => {
    if (user) {
      fetchUserTweets(user.id);
    }
  }, [user]);

  const fetchUserProfile = async () => {
    if (!username) return;
    
    try {
      setIsLoading(true);
      
      // If the username matches the current user, use current user data
      if (currentUser && username === currentUser.username) {
        setUser(currentUser);
        setIsFollowing(false); // Can't follow yourself
        setIsFollowedBy(false);
        return;
      }
      
      const userData = await userService.getUserByUsername(username);
      setUser(userData);
      setIsFollowing(userData.is_following);
      
      // Check if the profile user follows the current user
      if (currentUser) {
        await checkMutualFollowStatus(userData.id);
      }
    } catch (error: any) {
      console.error('Failed to fetch user profile:', error);
      toast({
        title: 'Error',
        description: 'Failed to load user profile. User may not exist.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const checkMutualFollowStatus = async (profileUserId: number) => {
    if (!currentUser) return;
    
    try {
      setIsCheckingMutualFollow(true);
      // Check if the profile user follows the current user
      const followingResponse = await userService.getFollowing(profileUserId);
      const followsCurrentUser = followingResponse.results.some(
        (followedUser) => followedUser.id === currentUser.id
      );
      setIsFollowedBy(followsCurrentUser);
    } catch (error: any) {
      console.error('Failed to check mutual follow status:', error);
    } finally {
      setIsCheckingMutualFollow(false);
    }
  };

  const fetchUserTweets = async (userId?: number) => {
    try {
      setIsLoadingTweets(true);
      const targetUserId = userId || user?.id;
      if (!targetUserId) return;
      
      const response = await tweetService.getUserTweets(targetUserId);
      setTweets(response.results);
    } catch (error: any) {
      console.error('Failed to fetch user tweets:', error);
      toast({
        title: 'Error',
        description: 'Failed to load tweets',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingTweets(false);
    }
  };

  const handleFollow = async () => {
    if (!user || !currentUser) return;
    
    try {
      if (isFollowing) {
        await userService.unfollowUser(user.id);
        setIsFollowing(false);
        setUser(prev => prev ? { ...prev, followers_count: prev.followers_count - 1 } : null);
        // Update mutual follow status
        if (currentUser) {
          await checkMutualFollowStatus(user.id);
        }
      } else {
        await userService.followUser(user.id);
        setIsFollowing(true);
        setUser(prev => prev ? { ...prev, followers_count: prev.followers_count + 1 } : null);
        // Update mutual follow status
        if (currentUser) {
          await checkMutualFollowStatus(user.id);
        }
      }
    } catch (error: any) {
      console.error('Failed to follow/unfollow user:', error);
      toast({
        title: 'Error',
        description: 'Failed to update follow status',
        variant: 'destructive',
      });
    }
  };

  const handleStartChat = async () => {
    if (!user || !currentUser) return;
    
    try {
      setIsStartingChat(true);
      
      // Create a conversation with a simple greeting message
      await messagingService.createConversation(
        user.id, 
        `Hi ${user.first_name || user.username}! 👋`
      );
      
      // Navigate to messages page
      navigate('/messages');
      
      toast({
        title: 'Success',
        description: `Started conversation with ${user.full_name}`,
      });
    } catch (error: any) {
      console.error('Failed to start conversation:', error);
      toast({
        title: 'Error',
        description: 'Failed to start conversation. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsStartingChat(false);
    }
  };
  const imageUrl = '/img.webp';

  if (isLoading || !user) {
    return (
      <div className="flex-1 border-r border-border">
        <div className="p-8 text-center text-muted-foreground">
          Loading profile...
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 border-r border-border">
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border p-4">
        <h2 className="text-xl font-bold">{user.full_name}</h2>
        <p className="text-sm text-muted-foreground">{tweets.length} tweets</p>
      </header>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div className={`h-48 rounded-lg bg-cover bg-center`}
        style={{ backgroundImage: `url(${imageUrl})` }}
        ></div>

        {/* Profile Info */}
        <div className="px-4 pb-4">
          <div className="flex justify-between items-start -mt-16 mb-4">
            <Avatar className="w-32 h-32 border-4 border-background bg-black">
              <AvatarImage src={user.profile_image_url} />
              <AvatarFallback className="text-3xl">{user.full_name?.[0] || user.username?.[0] || 'U'}</AvatarFallback>
            </Avatar>

            {currentUser && currentUser.id !== user.id && (
              <div className="flex gap-2 mt-16">
                <Button
                  variant={isFollowing ? 'outline' : 'default'}
                  onClick={handleFollow}
                >
                  {isFollowing ? 'Following' : 'Follow'} 
                </Button>
                
                {/* Show chat button only if both users follow each other */}
                {isFollowing && isFollowedBy && !isCheckingMutualFollow && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleStartChat}
                    disabled={isStartingChat}
                    title="Send message"
                  >
                    <MessageCircle className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </div>

          <div className="space-y-3">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                {user.full_name}
                {user.is_verified && (
                  <svg className="w-5 h-5 text-primary" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.5 12.5c0-1.58-.875-2.95-2.148-3.6.154-.435.238-.905.238-1.4 0-2.21-1.71-3.998-3.818-3.998-.47 0-.92.084-1.336.25C14.818 2.415 13.51 1.5 12 1.5s-2.816.917-3.437 2.25c-.415-.165-.866-.25-1.336-.25-2.11 0-3.818 1.79-3.818 4 0 .494.083.964.237 1.4-1.272.65-2.147 2.018-2.147 3.6 0 1.495.782 2.798 1.942 3.486-.02.17-.032.34-.032.514 0 2.21 1.708 4 3.818 4 .47 0 .92-.086 1.335-.25.62 1.334 1.926 2.25 3.437 2.25 1.512 0 2.818-.916 3.437-2.25.415.163.865.248 1.336.248 2.11 0 3.818-1.79 3.818-4 0-.174-.012-.344-.033-.513 1.158-.687 1.943-1.99 1.943-3.484zm-6.616-3.334l-4.334 6.5c-.145.217-.382.334-.625.334-.143 0-.288-.04-.416-.126l-.115-.094-2.415-2.415c-.293-.293-.293-.768 0-1.06s.768-.294 1.06 0l1.77 1.767 3.825-5.74c.23-.345.696-.436 1.04-.207.346.23.44.696.21 1.04z" />
                  </svg>
                )}
              </h1>
              <p className="text-muted-foreground">@{user.username}</p>
            </div>

            {user.bio && <p className="text-foreground">{user.bio}</p>}

            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              {user.date_joined && (
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>Joined {format(new Date(user.date_joined), 'MMMM yyyy')}</span>
                </div>
              )}
            </div>

            <div className="flex gap-6">
              <div>
                <span className="font-bold text-foreground">{user.following_count}</span>
                <span className="text-muted-foreground ml-1">Following</span>
              </div>
              <div>
                <span className="font-bold text-foreground">{user.followers_count}</span>
                <span className="text-muted-foreground ml-1">Followers</span>
              </div>
              {currentUser && currentUser.id !== user.id && isFollowing && isFollowedBy && (
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <MessageCircle className="w-3 h-3" />
                  <span>Can message</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tweets Tabs */}
        <Tabs defaultValue="tweets" className="w-full">
          <TabsList className="w-full h-14 rounded-none bg-transparent border-b border-border">
            <TabsTrigger
              value="tweets"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Tweets
            </TabsTrigger>
            <TabsTrigger
              value="replies"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Replies
            </TabsTrigger>
            <TabsTrigger
              value="media"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Media
            </TabsTrigger>
            <TabsTrigger
              value="likes"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Likes
            </TabsTrigger>
          </TabsList>

          <TabsContent value="tweets" className="mt-0">
            {isLoadingTweets ? (
              <div className="p-8 text-center text-muted-foreground">
                Loading tweets...
              </div>
            ) : tweets.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No tweets yet.
              </div>
            ) : (
              tweets.map((tweet) => (
                <TweetCard key={tweet.id} tweet={tweet} />
              ))
            )}
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  );
};

export default Profile;
