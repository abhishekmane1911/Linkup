import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Calendar, MessageCircle, Settings, Flag } from 'lucide-react';
import { User, Tweet } from '@/types';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import TweetCard from '@/components/tweet/TweetCard';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import EditProfileModal from '@/components/profile/EditProfileModal';
import ReportDialog from '@/components/moderation/ReportDialog';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { userService, UserProfile } from '@/services/userService';
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
  const [retweets, setRetweets] = useState<Tweet[]>([]);
  const [mediaTweets, setMediaTweets] = useState<Tweet[]>([]);
  const [likedTweets, setLikedTweets] = useState<Tweet[]>([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [isFollowedBy, setIsFollowedBy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingTweets, setIsLoadingTweets] = useState(true);
  const [isLoadingRetweets, setIsLoadingRetweets] = useState(false);
  const [isLoadingMedia, setIsLoadingMedia] = useState(false);
  const [isLoadingLikes, setIsLoadingLikes] = useState(false);
  const [isStartingChat, setIsStartingChat] = useState(false);
  const [isCheckingMutualFollow, setIsCheckingMutualFollow] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const { toast } = useToast();

  const handleProfileUpdate = (updatedUser: UserProfile) => {
    setUser(updatedUser as User);
  };

  useEffect(() => {
    if (username) {
      fetchUserProfile();
    } else if (currentUser) {
      
      setUser(currentUser);
      fetchUserTweets(currentUser.id);
    }
  }, [username, currentUser]);

  
  useEffect(() => {
    if (user) {
      fetchUserTweets(user.id);
    }
  }, [user]);

  const fetchUserProfile = async () => {
    if (!username) return;
    
    try {
      setIsLoading(true);
      
      
      if (currentUser && username === currentUser.username) {
        setUser(currentUser);
        setIsFollowing(false); 
        setIsFollowedBy(false);
        return;
      }
      
      const userData = await userService.getUserByUsername(username);
      setUser(userData);
      setIsFollowing(userData.is_following);
      
     
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

  const fetchUserRetweets = async (userId?: number) => {
    try {
      setIsLoadingRetweets(true);
      const targetUserId = userId || user?.id;
      if (!targetUserId) return;
      
      const response = await tweetService.getUserRetweets(targetUserId);
      setRetweets(response.results);
    } catch (error: any) {
      console.error('Failed to fetch user retweets:', error);
      toast({
        title: 'Error',
        description: 'Failed to load retweets',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingRetweets(false);
    }
  };

  const fetchUserMedia = async (userId?: number) => {
    try {
      setIsLoadingMedia(true);
      const targetUserId = userId || user?.id;
      if (!targetUserId) return;
      
      const response = await tweetService.getUserMedia(targetUserId);
      setMediaTweets(response.results);
    } catch (error: any) {
      console.error('Failed to fetch user media:', error);
      toast({
        title: 'Error',
        description: 'Failed to load media',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingMedia(false);
    }
  };

  const fetchUserLikes = async (userId?: number) => {
    try {
      setIsLoadingLikes(true);
      const targetUserId = userId || user?.id;
      if (!targetUserId) return;
      
      const response = await tweetService.getUserLikes(targetUserId);
      setLikedTweets(response.results);
    } catch (error: any) {
      console.error('Failed to fetch liked tweets:', error);
      toast({
        title: 'Error',
        description: 'Failed to load likes',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingLikes(false);
    }
  };

  const handleFollow = async () => {
    if (!user || !currentUser) return;
    
    try {
      if (isFollowing) {
        await userService.unfollowUser(user.id);
        setIsFollowing(false);
        setUser(prev => prev ? { ...prev, followers_count: prev.followers_count - 1 } : null);
       
        if (currentUser) {
          await checkMutualFollowStatus(user.id);
        }
      } else {
        await userService.followUser(user.id);
        setIsFollowing(true);
        setUser(prev => prev ? { ...prev, followers_count: prev.followers_count + 1 } : null);
        
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
      
      
      await messagingService.createConversation(
        user.id, 
        `Hi ${user.first_name || user.username}! 👋`
      );
      
     
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
        style={{ backgroundImage: `url(${user.banner_image_url ?user.banner_image_url : imageUrl})` }}
        ></div>

        {/* Profile Info */}
        <div className="px-4 pb-4">
          <div className="flex justify-between items-start -mt-16 mb-4">
            <Avatar className="w-32 h-32 border-4 border-background bg-black">
              <AvatarImage src={user.profile_image_url} />
              <AvatarFallback className="text-3xl">{user.full_name?.[0] || user.username?.[0] || 'U'}</AvatarFallback>
            </Avatar>

            {currentUser && currentUser.id === user.id ? (
              <Button
                variant="outline"
                onClick={() => setIsEditModalOpen(true)}
                className="mt-16 gap-2"
              >
                <Settings className="w-4 h-4" />
                Edit Profile
              </Button>
            ) : currentUser && currentUser.id !== user.id && (
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

                {/* Report user button */}
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowReportDialog(true)}
                  title="Report user"
                >
                  <Flag className="w-4 h-4" />
                </Button>
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
              value="retweets"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
              onClick={() => !retweets.length && user && fetchUserRetweets(user.id)}
            >
              Retweets
            </TabsTrigger>
            <TabsTrigger
              value="media"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
              onClick={() => !mediaTweets.length && user && fetchUserMedia(user.id)}
            >
              Media
            </TabsTrigger>
            <TabsTrigger
              value="likes"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
              onClick={() => !likedTweets.length && user && fetchUserLikes(user.id)}
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

          <TabsContent value="retweets" className="mt-0">
            {isLoadingRetweets ? (
              <div className="p-8 text-center text-muted-foreground">
                Loading retweets...
              </div>
            ) : retweets.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No retweets yet.
              </div>
            ) : (
              retweets.map((retweet) => (
                <TweetCard key={retweet.id} tweet={retweet} />
              ))
            )}
          </TabsContent>

          <TabsContent value="media" className="mt-0">
            {isLoadingMedia ? (
              <div className="p-8 text-center text-muted-foreground">
                Loading media...
              </div>
            ) : mediaTweets.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No media tweets yet.
              </div>
            ) : (
              mediaTweets.map((tweet) => (
                <TweetCard key={tweet.id} tweet={tweet} />
              ))
            )}
          </TabsContent>

          <TabsContent value="likes" className="mt-0">
            {isLoadingLikes ? (
              <div className="p-8 text-center text-muted-foreground">
                Loading likes...
              </div>
            ) : likedTweets.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No liked tweets yet.
              </div>
            ) : (
              likedTweets.map((tweet) => (
                <TweetCard key={tweet.id} tweet={tweet} />
              ))
            )}
          </TabsContent>
        </Tabs>

        
      </motion.div>

      {/* Edit Profile Modal */}
      {currentUser && currentUser.id === user.id && (
        <EditProfileModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          user={user as UserProfile}
          onUpdate={handleProfileUpdate}
        />
      )}

      {/* Report User Dialog */}
      {user && currentUser && currentUser.id !== user.id && (
        <ReportDialog
          isOpen={showReportDialog}
          onClose={() => setShowReportDialog(false)}
          contentType="user"
          objectId={user.id}
          objectDescription={`@${user.username}`}
        />
      )}
    </div>
  );
};

export default Profile;
