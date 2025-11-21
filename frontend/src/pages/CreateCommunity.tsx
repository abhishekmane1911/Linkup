import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Globe, Lock, Loader2 } from 'lucide-react';
import { communityService } from '@/services/communityService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useToast } from '@/hooks/use-toast';
import { motion } from 'framer-motion';

const CreateCommunity = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    privacy: 'public' as 'public' | 'private',
    rules: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Community name is required';
    } else if (formData.name.length < 3) {
      newErrors.name = 'Community name must be at least 3 characters';
    } else if (formData.name.length > 50) {
      newErrors.name = 'Community name must be less than 50 characters';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters';
    } else if (formData.description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters';
    }

    if (formData.rules && formData.rules.length > 1000) {
      newErrors.rules = 'Rules must be less than 1000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const community = await communityService.createCommunity({
        name: formData.name.trim(),
        description: formData.description.trim(),
        privacy: formData.privacy,
        rules: formData.rules.trim() || undefined
      });

      toast({
        title: 'Community created!',
        description: `${community.name} has been created successfully.`,
      });

      navigate(`/communities/${community.id}`);
    } catch (error: any) {
      console.error('Failed to create community:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to create community',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

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
          <h1 className="text-xl font-bold">Create Community</h1>
        </div>
      </header>

      <div className="p-6 max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Create a New Community</CardTitle>
              <CardDescription>
                Build a space for people to connect around shared interests.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Community Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">Community Name *</Label>
                  <Input
                    id="name"
                    placeholder="Enter community name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className={errors.name ? 'border-red-500' : ''}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-500">{errors.name}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {formData.name.length}/50 characters
                  </p>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe what your community is about"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    className={`min-h-[100px] ${errors.description ? 'border-red-500' : ''}`}
                  />
                  {errors.description && (
                    <p className="text-sm text-red-500">{errors.description}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {formData.description.length}/500 characters
                  </p>
                </div>

                {/* Privacy Settings */}
                <div className="space-y-3">
                  <Label>Privacy Settings</Label>
                  <RadioGroup
                    value={formData.privacy}
                    onValueChange={(value) => handleInputChange('privacy', value)}
                  >
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <RadioGroupItem value="public" id="public" />
                      <Globe className="w-4 h-4 text-muted-foreground" />
                      <div className="flex-1">
                        <Label htmlFor="public" className="font-medium cursor-pointer">
                          Public
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Anyone can see and join this community
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <RadioGroupItem value="private" id="private" />
                      <Lock className="w-4 h-4 text-muted-foreground" />
                      <div className="flex-1">
                        <Label htmlFor="private" className="font-medium cursor-pointer">
                          Private
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Only members can see posts and join by invitation
                        </p>
                      </div>
                    </div>
                  </RadioGroup>
                </div>

                {/* Community Rules */}
                <div className="space-y-2">
                  <Label htmlFor="rules">Community Rules (Optional)</Label>
                  <Textarea
                    id="rules"
                    placeholder="Set guidelines for your community members"
                    value={formData.rules}
                    onChange={(e) => handleInputChange('rules', e.target.value)}
                    className={`min-h-[120px] ${errors.rules ? 'border-red-500' : ''}`}
                  />
                  {errors.rules && (
                    <p className="text-sm text-red-500">{errors.rules}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {formData.rules.length}/1000 characters
                  </p>
                </div>

                {/* Submit Button */}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate('/communities')}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 gap-2"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      'Create Community'
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default CreateCommunity;
