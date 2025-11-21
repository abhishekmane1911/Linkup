import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Lock, Settings } from 'lucide-react';
import { Community, communityService } from '@/services/communityService';
import { Tweet } from '@/types';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import TweetCard from '@/components/tweet/TweetCard';
import TweetComposer from '@/components/tweet/TweetComposer';
import EditCommunityModal from '@/components/community/EditCommunityModal';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { motion } from 'framer-motion';

const CommunityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [community, setCommunity] = useState<Community | null>(null);
  const [feed, setFeed] = useState<Tweet[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingFeed, setIsLoadingFeed] = useState(true);
  const [isJoining, setIsJoining] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { toast } = useToast();

  const handleCommunityUpdate = (updatedCommunity: Community) => {
    setCommunity(updatedCommunity);
  };

  useEffect(() => {
    if (id) {
      fetchCommunity();
      fetchCommunityFeed();
    }
  }, [id]);

  const fetchCommunity = async () => {
    try {
      setIsLoading(true);
      const data = await communityService.getCommunity(Number(id));
      setCommunity(data);
    } catch (error) {
      console.error('Failed to fetch community:', error);
      toast({
        title: 'Error',
        description: 'Failed to load community',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCommunityFeed = async () => {
    try {
      setIsLoadingFeed(true);
      const response = await communityService.getCommunityFeed(Number(id));
      setFeed(response.results || []);
    } catch (error) {
      console.error('Failed to fetch community feed:', error);
      toast({
        title: 'Error',
        description: 'Failed to load community feed',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingFeed(false);
    }
  };

  const handleJoinLeave = async () => {
    if (!community) return;

    try {
      setIsJoining(true);
      if (community.is_member) {
        await communityService.leaveCommunity(community.id);
        setCommunity({
          ...community,
          is_member: false,
          members_count: community.members_count - 1,
        });
        toast({
          title: 'Success',
          description: 'Left community successfully',
        });
      } else {
        await communityService.joinCommunity(community.id);
        setCommunity({
          ...community,
          is_member: true,
          members_count: community.members_count + 1,
        });
        toast({
          title: 'Success',
          description: 'Joined community successfully',
        });
      }
    } catch (error: any) {
      console.error('Failed to join/leave community:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to update membership',
        variant: 'destructive',
      });
    } finally {
      setIsJoining(false);
    }
  };

  if (isLoading || !community) {
    return (
      <div className="flex-1 border-r border-border p-8 text-center text-muted-foreground">
        Loading community...
      </div>
    );
  }

  const isOwner = currentUser?.id === community.owner.id;
  const canManage = isOwner || community.user_role === 'admin';

  return (
    <div className="flex-1 border-r border-border">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border p-4">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/communities')}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold">{community.name}</h1>
            <p className="text-sm text-muted-foreground">
              {community.members_count} members
            </p>
          </div>
        </div>
      </header>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        {/* Banner */}
        <div
          className="h-48 bg-gradient-to-r from-primary/20 to-primary/40 bg-cover bg-center"
          style={
            community.banner_image_url
              ? { backgroundImage: `url(${community.banner_image_url})` }
              : undefined
          }
        />

        {/* Community Info */}
        <div className="px-4 py-6 border-b border-border">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h2 className="text-2xl font-bold">{community.name}</h2>
                {community.privacy === 'private' && (
                  <Lock className="w-5 h-5 text-muted-foreground" />
                )}
              </div>
              <p className="text-muted-foreground mb-2">
                Created by @{community.owner.username}
              </p>
              {community.description && (
                <p className="text-foreground mb-4">{community.description}</p>
              )}
            </div>

            <div className="flex gap-2">
              {canManage && (
                <Button 
                  variant="outline" 
                  size="icon"
                  onClick={() => setIsEditModalOpen(true)}
                  title="Edit community"
                >
                  <Settings className="w-4 h-4" />
                </Button>
              )}
              <Button
                variant={community.is_member ? 'outline' : 'default'}
                onClick={handleJoinLeave}
                disabled={isJoining}
              >
                {community.is_member ? 'Leave' : 'Join'}
              </Button>
            </div>
          </div>

          <div className="flex gap-6 text-sm">
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4 text-muted-foreground" />
              <span className="font-semibold">{community.members_count}</span>
              <span className="text-muted-foreground">members</span>
            </div>
            <div>
              <span className="font-semibold">{community.posts_count}</span>
              <span className="text-muted-foreground ml-1">posts</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="feed" className="w-full">
          <TabsList className="w-full h-14 rounded-none bg-transparent border-b border-border">
            <TabsTrigger
              value="feed"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Feed
            </TabsTrigger>
            <TabsTrigger
              value="about"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              About
            </TabsTrigger>
          </TabsList>

          <TabsContent value="feed" className="mt-0">
            {/* Tweet Composer for members */}
            {community.is_member && (
              <TweetComposer 
                onTweetPosted={fetchCommunityFeed}
                communityId={community.id}
                placeholder={`Share something with ${community.name}...`}
              />
            )}

            {isLoadingFeed ? (
              <div className="p-8 text-center text-muted-foreground">
                Loading feed...
              </div>
            ) : feed.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <p>No posts yet in this community</p>
                {community.is_member && (
                  <p className="text-sm mt-2">Be the first to post!</p>
                )}
              </div>
            ) : (
              <div className="divide-y divide-border">
                {feed.map(tweet => (
                  <TweetCard key={tweet.id} tweet={tweet} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="about" className="mt-0 p-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-2">Description</h3>
                <p className="text-muted-foreground">
                  {community.description || 'No description provided'}
                </p>
              </div>

              {community.rules && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Rules</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">
                    {community.rules}
                  </p>
                </div>
              )}

              <div>
                <h3 className="text-lg font-semibold mb-2">Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Privacy</span>
                    <span className="font-medium capitalize">{community.privacy}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created</span>
                    <span className="font-medium">
                      {new Date(community.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>

      {/* Edit Community Modal */}
      {canManage && (
        <EditCommunityModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          community={community}
          onUpdate={handleCommunityUpdate}
        />
      )}
    </div>
  );
};

export default CommunityDetail;
