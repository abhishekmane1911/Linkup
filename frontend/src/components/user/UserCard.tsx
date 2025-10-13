import { useState } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { userService } from '@/services/userService';
import { useToast } from '@/hooks/use-toast';

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

interface UserCardProps {
  user: UserProfile;
  onUserUpdate?: (updatedUser: UserProfile) => void;
  showFollowButton?: boolean;
}

const UserCard = ({ user, onUserUpdate, showFollowButton = true }: UserCardProps) => {
  const [isFollowing, setIsFollowing] = useState(user.is_following);
  const [followersCount, setFollowersCount] = useState(user.followers_count);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleUserClick = () => {
    navigate(`/profile/${user.username}`);
  };

  const handleFollowUser = async (e: React.MouseEvent) => {
    e.stopPropagation();
    
    try {
      setIsLoading(true);
      if (isFollowing) {
        await userService.unfollowUser(user.id);
        setIsFollowing(false);
        setFollowersCount(prev => prev - 1);
      } else {
        await userService.followUser(user.id);
        setIsFollowing(true);
        setFollowersCount(prev => prev + 1);
      }
      
      // Notify parent component of the update
      if (onUserUpdate) {
        onUserUpdate({
          ...user,
          is_following: !isFollowing,
          followers_count: isFollowing ? followersCount - 1 : followersCount + 1
        });
      }
    } catch (error: any) {
      console.error('Failed to follow/unfollow user:', error);
      toast({
        title: 'Error',
        description: 'Failed to update follow status',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
    >
      <div 
        className="flex items-center gap-3 flex-1 cursor-pointer"
        onClick={handleUserClick}
      >
        <Avatar className="w-12 h-12">
          <AvatarImage src={user.profile_image_url} />
          <AvatarFallback>{user.full_name?.[0] || user.username?.[0] || 'U'}</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <p className="font-bold">{user.full_name}</p>
            {user.is_verified && (
              <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.5 12.5c0-1.58-.875-2.95-2.148-3.6.154-.435.238-.905.238-1.4 0-2.21-1.71-3.998-3.818-3.998-.47 0-.92.084-1.336.25C14.818 2.415 13.51 1.5 12 1.5s-2.816.917-3.437 2.25c-.415-.165-.866-.25-1.336-.25-2.11 0-3.818 1.79-3.818 4 0 .494.083.964.237 1.4-1.272.65-2.147 2.018-2.147 3.6 0 1.495.782 2.798 1.942 3.486-.02.17-.032.34-.032.514 0 2.21 1.708 4 3.818 4 .47 0 .92-.086 1.335-.25.62 1.334 1.926 2.25 3.437 2.25 1.512 0 2.818-.916 3.437-2.25.415.163.865.248 1.336.248 2.11 0 3.818-1.79 3.818-4 0-.174-.012-.344-.033-.513 1.158-.687 1.943-1.99 1.943-3.484zm-6.616-3.334l-4.334 6.5c-.145.217-.382.334-.625.334-.143 0-.288-.04-.416-.126l-.115-.094-2.415-2.415c-.293-.293-.293-.768 0-1.06s.768-.294 1.06 0l1.77 1.767 3.825-5.74c.23-.345.696-.436 1.04-.207.346.23.44.696.21 1.04z" />
              </svg>
            )}
          </div>
          <p className="text-sm text-muted-foreground">@{user.username}</p>
          <p className="text-sm text-muted-foreground">
            {followersCount} followers
          </p>
        </div>
      </div>
      {showFollowButton && (
        <Button
          variant={isFollowing ? 'outline' : 'default'}
          size="sm"
          onClick={handleFollowUser}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : isFollowing ? 'Following' : 'Follow'}
        </Button>
      )}
    </motion.div>
  );
};

export default UserCard;