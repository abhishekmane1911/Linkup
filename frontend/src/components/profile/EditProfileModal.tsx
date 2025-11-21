import { useState } from 'react';
import { X } from 'lucide-react';
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
import { userService, UserProfile } from '@/services/userService';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserProfile;
  onUpdate: (updatedUser: UserProfile) => void;
}

const EditProfileModal = ({ isOpen, onClose, user, onUpdate }: EditProfileModalProps) => {
  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    bio: user.bio || '',
    location: user.location || '',
    website: user.website || '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const { updateUser } = useAuth();

  // Debug: Log user data
  console.log('EditProfileModal - User data:', user);
  console.log('Profile image URL:', user.profile_image_url);
  console.log('Banner image URL:', user.banner_image_url);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleProfileImageUpload = async (file: File) => {
    try {
      console.log('Uploading profile image...');
      const updatedUser = await userService.updateProfileImage(file);
      console.log('Profile image uploaded, response:', updatedUser);
      onUpdate(updatedUser);
      updateUser(updatedUser);
      toast({
        title: 'Success',
        description: 'Profile image updated successfully',
      });
    } catch (error) {
      console.error('Profile image upload failed:', error);
      throw error; // Re-throw so ImageUpload component can handle it
    }
  };

  const handleBannerImageUpload = async (file: File) => {
    try {
      console.log('Uploading banner image...');
      const updatedUser = await userService.updateBannerImage(file);
      console.log('Banner image uploaded, response:', updatedUser);
      onUpdate(updatedUser);
      updateUser(updatedUser);
      toast({
        title: 'Success',
        description: 'Banner image updated successfully',
      });
    } catch (error) {
      console.error('Banner image upload failed:', error);
      throw error; // Re-throw so ImageUpload component can handle it
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await api.patch<UserProfile>('/auth/profile/', formData);
      onUpdate(response.data);
      updateUser(response.data);
      
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully',
      });
      onClose();
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      toast({
        title: 'Update failed',
        description: error.response?.data?.error || 'Failed to update profile',
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
          <DialogTitle>Edit Profile</DialogTitle>
          <DialogDescription>
            Update your profile information and images
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Banner Image */}
          <div className="space-y-2">
            <Label>Banner Image</Label>
            <ImageUpload
              currentImage={user.banner_image_url}
              onUpload={handleBannerImageUpload}
              type="banner"
            />
          </div>

          {/* Profile Image */}
          <div className="space-y-2">
            <Label>Profile Image</Label>
            <ImageUpload
              currentImage={user.profile_image_url}
              onUpload={handleProfileImageUpload}
              type="profile"
            />
          </div>

          {/* Name Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">First Name</Label>
              <Input
                id="first_name"
                value={formData.first_name}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                placeholder="First name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Last Name</Label>
              <Input
                id="last_name"
                value={formData.last_name}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                placeholder="Last name"
              />
            </div>
          </div>

          {/* Bio */}
          <div className="space-y-2">
            <Label htmlFor="bio">Bio</Label>
            <Textarea
              id="bio"
              value={formData.bio}
              onChange={(e) => handleInputChange('bio', e.target.value)}
              placeholder="Tell us about yourself"
              className="min-h-[100px]"
              maxLength={160}
            />
            <p className="text-xs text-muted-foreground">
              {formData.bio.length}/160 characters
            </p>
          </div>

          {/* Location */}
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              placeholder="Where are you from?"
            />
          </div>

          {/* Website */}
          <div className="space-y-2">
            <Label htmlFor="website">Website</Label>
            <Input
              id="website"
              type="url"
              value={formData.website}
              onChange={(e) => handleInputChange('website', e.target.value)}
              placeholder="https://yourwebsite.com"
            />
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

export default EditProfileModal;
