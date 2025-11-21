import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { reportService, ReportType } from '@/services/reportService';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface ReportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  contentType: 'tweet' | 'user';
  objectId: number;
  objectDescription?: string;
}

const REPORT_TYPES: { value: ReportType; label: string; description: string }[] = [
  { value: 'spam', label: 'Spam', description: 'Repetitive or unsolicited content' },
  { value: 'harassment', label: 'Harassment', description: 'Bullying or targeted harassment' },
  { value: 'hate_speech', label: 'Hate Speech', description: 'Hateful or discriminatory content' },
  { value: 'violence', label: 'Violence', description: 'Threats or graphic violence' },
  { value: 'inappropriate_content', label: 'Inappropriate Content', description: 'NSFW or offensive material' },
  { value: 'copyright', label: 'Copyright Violation', description: 'Unauthorized use of copyrighted material' },
  { value: 'fake_news', label: 'Fake News', description: 'Misinformation or false claims' },
  { value: 'impersonation', label: 'Impersonation', description: 'Pretending to be someone else' },
  { value: 'other', label: 'Other', description: 'Other violations' },
];

const ReportDialog = ({ isOpen, onClose, contentType, objectId, objectDescription }: ReportDialogProps) => {
  const [reportType, setReportType] = useState<ReportType>('spam');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!description.trim()) {
      toast({
        title: 'Description required',
        description: 'Please provide details about why you\'re reporting this content',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await reportService.createReport({
        content_type: contentType,
        object_id: objectId,
        report_type: reportType,
        description: description.trim(),
      });

      toast({
        title: 'Report submitted',
        description: 'Thank you for helping keep our community safe. We\'ll review this report.',
      });

      // Reset form and close
      setReportType('spam');
      setDescription('');
      onClose();
    } catch (error: any) {
      console.error('Failed to submit report:', error);
      toast({
        title: 'Failed to submit report',
        description: error.response?.data?.error || 'Please try again later',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setReportType('spam');
      setDescription('');
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Report {contentType === 'tweet' ? 'Tweet' : 'User'}</DialogTitle>
          <DialogDescription>
            Help us understand what's wrong with this {contentType}.
            {objectDescription && (
              <span className="block mt-2 text-sm italic">"{objectDescription}"</span>
            )}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Report Type Selection */}
          <div className="space-y-3">
            <Label>What's the issue?</Label>
            <RadioGroup value={reportType} onValueChange={(value) => setReportType(value as ReportType)}>
              {REPORT_TYPES.map((type) => (
                <div key={type.value} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-accent/50 transition-colors">
                  <RadioGroupItem value={type.value} id={type.value} className="mt-1" />
                  <div className="flex-1">
                    <Label htmlFor={type.value} className="font-medium cursor-pointer">
                      {type.label}
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      {type.description}
                    </p>
                  </div>
                </div>
              ))}
            </RadioGroup>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Additional Details *</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Please provide specific details about this violation..."
              className="min-h-[120px]"
              maxLength={1000}
              required
            />
            <p className="text-xs text-muted-foreground">
              {description.length}/1000 characters
            </p>
          </div>

          {/* Action Buttons */}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || !description.trim()}
              className="gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Report'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ReportDialog;
