import { useState, useRef } from 'react';
import { Camera, Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { motion, AnimatePresence } from 'framer-motion';

interface ImageUploadProps {
  currentImage?: string;
  onUpload: (file: File) => Promise<void>;
  type: 'profile' | 'banner';
  className?: string;
}

const ImageUpload = ({ currentImage, onUpload, type, className = '' }: ImageUploadProps) => {
  const [isUploading, setIsUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Debug: Log current image
  console.log(`ImageUpload (${type}) - currentImage:`, currentImage);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: 'Invalid file type',
        description: 'Please select an image file',
        variant: 'destructive',
      });
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Please select an image smaller than 5MB',
        variant: 'destructive',
      });
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload
    setIsUploading(true);
    try {
      console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);
      await onUpload(file);
      console.log('Upload successful');
      toast({
        title: 'Success',
        description: `${type === 'profile' ? 'Profile' : 'Banner'} image updated successfully`,
      });
      setPreviewUrl(null);
    } catch (error: any) {
      console.error('Failed to upload image:', error);
      console.error('Error response:', error.response);
      toast({
        title: 'Upload failed',
        description: error.response?.data?.error || error.message || 'Failed to upload image',
        variant: 'destructive',
      });
      setPreviewUrl(null);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemovePreview = () => {
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const displayImage = previewUrl || currentImage;
  const isProfile = type === 'profile';

  return (
    <div
      className={`relative group ${className}`}
      onMouseEnter={() => setShowOverlay(true)}
      onMouseLeave={() => setShowOverlay(false)}
    >
      {/* Image Display */}
      <div
        className={`relative overflow-hidden bg-muted ${
          isProfile
            ? 'w-32 h-32 rounded-full'
            : 'w-full h-48 rounded-lg'
        }`}
      >
        {displayImage ? (
          <img
            src={displayImage}
            alt={`${type} image`}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/20 to-primary/40">
            <Camera className="w-8 h-8 text-muted-foreground" />
          </div>
        )}

        {/* Overlay */}
        <AnimatePresence>
          {(showOverlay || isUploading) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50 flex items-center justify-center"
            >
              {isUploading ? (
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              ) : (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  className="gap-2"
                >
                  <Camera className="w-4 h-4" />
                  Change
                </Button>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Remove Preview Button */}
        {previewUrl && !isUploading && (
          <Button
            variant="destructive"
            size="icon"
            className="absolute top-2 right-2 h-8 w-8"
            onClick={handleRemovePreview}
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileSelect}
        disabled={isUploading}
      />

      {/* Upload Button (visible when no image) */}
      {!displayImage && !isUploading && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          className="absolute bottom-2 right-2 gap-2"
        >
          <Camera className="w-4 h-4" />
          Upload
        </Button>
      )}
    </div>
  );
};

export default ImageUpload;
