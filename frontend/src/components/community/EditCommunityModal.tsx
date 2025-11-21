import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import ImageUpload from '@/components/common/ImageUpload';
import { communityService, Community } from '@/services/communityService';
import { useToast } from '@/hooks/use-toast';

interface EditCommunityModalProps {
  isOpen: boolean;
  onClose: () => void;
  community: Community;
  onUpdate: (updatedCommunity: Community) => void;
}

const EditCommunityModal = ({ isOpen, onClose, community, onUpdate }: EditCommunityModalProps) => {
  const [formData, setFormData] = useState({
    name: community.name || '',
    description: community.description || '',
    rules: community.rules || '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleBannerImageUpload = async (file: File) => {
    const updatedCommunity = await communityService.updateCommunityBanner(community.id, file);
    onUpdate(updatedCommunity);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const updatedCommunity = await communityService.updateCommunity(community.id, formData);
      onUpdate(updatedCommunity);
      
      toast({
        title: 'Community updated',
        description: 'Community settings have been updated successfully',
      });
      onClose();
    } catch (error: any) {
      console.error('Failed to update community:', error);
      toast({
        title: 'Update failed',
        description: error.response?.data?.error || 'Failed to update community',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Community</DialogTitle>
          <DialogDescription>
            Update your community information and banner image
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Banner Image */}
          <div className="space-y-2">
            <Label>Banner Image</Label>
            <ImageUpload
              currentImage={community.banner_image_url}
              onUpload={handleBannerImageUpload}
              type="banner"
            />
          </div>

          {/* Community Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Community Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Community name"
              maxLength={50}
            />
            <p className="text-xs text-muted-foreground">
              {formData.name.length}/50 characters
            </p>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Describe your community"
              className="min-h-[100px]"
              maxLength={500}
            />
            <p className="text-xs text-muted-foreground">
              {formData.description.length}/500 characters
            </p>
          </div>

          {/* Rules */}
          <div className="space-y-2">
            <Label htmlFor="rules">Community Rules</Label>
            <Textarea
              id="rules"
              value={formData.rules}
              onChange={(e) => handleInputChange('rules', e.target.value)}
              placeholder="Set guidelines for your community"
              className="min-h-[120px]"
              maxLength={1000}
            />
            <p className="text-xs text-muted-foreground">
              {formData.rules.length}/1000 characters
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EditCommunityModal;
