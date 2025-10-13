import { useState, useRef } from 'react';
import { Image, Smile, Calendar, MapPin, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAuth } from '@/contexts/AuthContext';
import { tweetService } from '@/services/tweetService';
import { useToast } from '@/hooks/use-toast';

interface TweetComposerProps {
  onTweetPosted?: () => void;
  placeholder?: string;
  autoFocus?: boolean;
  parentTweetId?: number;
}

const TweetComposer = ({ onTweetPosted, placeholder = "What's happening?", autoFocus, parentTweetId }: TweetComposerProps) => {
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const maxLength = 280;

  const handleSubmit = async () => {
    if (!content.trim() || isLoading) return;

    setIsLoading(true);
    try {
      await tweetService.createTweet({
        content: content.trim(),
        parent_tweet: parentTweetId,
        media_files: mediaFiles.length > 0 ? mediaFiles : undefined,
      });
      
      setContent('');
      setMediaFiles([]);
      onTweetPosted?.();
      
      toast({
        title: 'Tweet posted!',
        description: 'Your tweet has been posted successfully.',
      });
    } catch (error: any) {
      console.error('Failed to post tweet:', error);
      toast({
        title: 'Failed to post tweet',
        description: error.response?.data?.error?.message || 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length > 0) {
      setMediaFiles(prev => [...prev, ...imageFiles].slice(0, 4)); // Max 4 images
    }
  };

  const removeMedia = (index: number) => {
    setMediaFiles(prev => prev.filter((_, i) => i !== index));
  };

  const remainingChars = maxLength - content.length;
  const isOverLimit = remainingChars < 0;

  return (
    <div className="border-b border-border p-4">
      <div className="flex gap-3">
        <Avatar className="w-12 h-12">
          <AvatarImage src={user?.profile_image_url} />
          <AvatarFallback>{user?.full_name?.[0]}</AvatarFallback>
        </Avatar>

        <div className="flex-1">
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={placeholder}
            className="min-h-[100px] resize-none border-0 focus-visible:ring-0 text-lg p-0"
            autoFocus={autoFocus}
            disabled={isLoading}
          />

          {/* Media Preview */}
          {mediaFiles.length > 0 && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              {mediaFiles.map((file, index) => (
                <div key={index} className="relative">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Upload ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <Button
                    variant="secondary"
                    size="icon"
                    className="absolute top-1 right-1 h-6 w-6"
                    onClick={() => removeMedia(index)}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={handleImageUpload}
          />

          <div className="flex items-center justify-between mt-4">
            <div className="flex gap-1">
              <Button 
                variant="ghost" 
                size="icon" 
                className="text-primary hover:bg-primary/10"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading || mediaFiles.length >= 4}
              >
                <Image className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-primary hover:bg-primary/10" disabled={isLoading}>
                <Smile className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-primary hover:bg-primary/10" disabled={isLoading}>
                <Calendar className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-primary hover:bg-primary/10" disabled={isLoading}>
                <MapPin className="w-5 h-5" />
              </Button>
            </div>

            <div className="flex items-center gap-4">
              <span className={`text-sm ${isOverLimit ? 'text-destructive' : 'text-muted-foreground'}`}>
                {remainingChars}
              </span>
              <Button
                onClick={handleSubmit}
                disabled={!content.trim() || isOverLimit || isLoading}
                className="rounded-full px-6 font-bold"
              >
                {isLoading ? 'Posting...' : parentTweetId ? 'Reply' : 'Tweet'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TweetComposer;
