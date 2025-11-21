import { Users, Lock } from 'lucide-react';
import { Community } from '@/services/communityService';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface CommunityCardProps {
  community: Community;
  onJoin?: (communityId: number) => void;
  onLeave?: (communityId: number) => void;
  isLoading?: boolean;
}

const CommunityCard = ({ community, onJoin, onLeave, isLoading }: CommunityCardProps) => {
  const navigate = useNavigate();

  const handleCardClick = () => {
    navigate(`/communities/${community.id}`);
  };

  const handleJoinLeave = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (community.is_member && onLeave) {
      onLeave(community.id);
    } else if (!community.is_member && onJoin) {
      onJoin(community.id);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
        onClick={handleCardClick}
      >
        {/* Banner */}
        <div
          className="h-32 bg-gradient-to-r from-primary/20 to-primary/40 bg-cover bg-center"
          style={
            community.banner_image_url
              ? { backgroundImage: `url(${community.banner_image_url})` }
              : undefined
          }
        />

        {/* Content */}
        <div className="p-4">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold">{community.name}</h3>
                {community.privacy === 'private' && (
                  <Lock className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                by @{community.owner.username}
              </p>
            </div>

            <Button
              size="sm"
              variant={community.is_member ? 'outline' : 'default'}
              onClick={handleJoinLeave}
              disabled={isLoading}
            >
              {community.is_member ? 'Joined' : 'Join'}
            </Button>
          </div>

          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
            {community.description || 'No description'}
          </p>

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              <span>{community.members_count} members</span>
            </div>
            <div>
              <span>{community.posts_count} posts</span>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

export default CommunityCard;
