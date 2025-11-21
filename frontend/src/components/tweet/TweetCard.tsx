import { useState, lazy, Suspense } from "react";
import {
  Heart,
  Repeat2,
  MessageCircle,
  Bookmark,
  MoreHorizontal,
  Loader2,
  Trash2,
  Flag,
} from "lucide-react";
import { Tweet } from "@/types";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { motion, AnimatePresence } from "framer-motion";
import { formatDistanceToNow } from "date-fns";
import { tweetService } from "@/services/tweetService";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import ReportDialog from "@/components/moderation/ReportDialog";

const TweetReplies = lazy(() => import("./TweetReplies"));

interface TweetCardProps {
  tweet: Tweet;
  nestingLevel?: number;
  onDelete?: (tweetId: number) => void;
}

const TweetCard = ({ tweet, nestingLevel = 0, onDelete }: TweetCardProps) => {
  const disableReplies = nestingLevel >= 2;
  const [liked, setLiked] = useState(tweet.is_liked);
  const [retweeted, setRetweeted] = useState(tweet.is_retweeted);
  const [bookmarked, setBookmarked] = useState(tweet.is_bookmarked);
  const [likesCount, setLikesCount] = useState(tweet.likes_count);
  const [retweetsCount, setRetweetsCount] = useState(tweet.retweets_count);
  const [replyCount, setReplyCount] = useState(tweet.reply_count);
  const [showReplies, setShowReplies] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [isDeleted, setIsDeleted] = useState(false);
  const { toast } = useToast();
  const { user: currentUser } = useAuth();

  const isOwnTweet = currentUser?.id === tweet.author?.id;

  const handleLike = async () => {
    if (isLoading) return;

    setIsLoading(true);
    const previousLiked = liked;
    const previousCount = likesCount;

    setLiked(!liked);
    setLikesCount(liked ? likesCount - 1 : likesCount + 1);

    try {
      if (liked) {
        const response = await tweetService.unlikeTweet(tweet.id);
        setLikesCount(response.likes_count);
      } else {
        const response = await tweetService.likeTweet(tweet.id);
        setLikesCount(response.likes_count);
      }
    } catch (error) {
      // Revert on error
      setLiked(previousLiked);
      setLikesCount(previousCount);
      toast({
        title: "Error",
        description: "Failed to update like status",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    if (isDeleting) return;

  
    if (!tweet.id || typeof tweet.id !== 'number') {
      console.error('Invalid tweet ID:', tweet.id);
      toast({
        title: "Error",
        description: "Invalid tweet ID. Cannot delete.",
        variant: "destructive",
      });
      setShowDeleteDialog(false);
      return;
    }

    setIsDeleting(true);
    setShowDeleteDialog(false);

    try {
      console.log('Deleting tweet with ID:', tweet.id);
      console.log('Full tweet object:', tweet);
      await tweetService.deleteTweet(tweet.id);
      console.log('Tweet deleted successfully');
      
      
      setIsDeleted(true);
      
      
      if (onDelete) {
        onDelete(tweet.id);
      }

      toast({
        title: "Tweet deleted",
        description: "Your tweet has been deleted successfully",
      });
    } catch (error: any) {
      console.error("Failed to delete tweet:", error);
      console.error("Error response:", error.response);
      console.error("Error status:", error.response?.status);
      console.error("Error data:", error.response?.data);
      
      
      let errorMessage = "Failed to delete tweet. Please try again.";
      
      if (error.response?.status === 404) {
        errorMessage = "Tweet not found. It may have already been deleted.";
      } else if (error.response?.status === 403) {
        errorMessage = "You don't have permission to delete this tweet.";
      } else if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.error) {
          errorMessage = typeof errorData.error === 'string' 
            ? errorData.error 
            : errorData.error.message || errorMessage;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  const handleRetweet = async () => {
    if (isLoading) return;

    setIsLoading(true);
    const previousRetweeted = retweeted;
    const previousCount = retweetsCount;

    setRetweeted(!retweeted);
    setRetweetsCount(retweeted ? retweetsCount - 1 : retweetsCount + 1);

    try {
      if (retweeted) {
        const response = await tweetService.unretweetTweet(tweet.id);
        setRetweetsCount(response.retweets_count);
      } else {
        const response = await tweetService.retweetTweet(tweet.id);
        setRetweetsCount(response.retweets_count);
      }
    } catch (error) {
      setRetweeted(previousRetweeted);
      setRetweetsCount(previousCount);
      toast({
        title: "Error",
        description: "Failed to update retweet status",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBookmark = async () => {
    if (isLoading) return;

    setIsLoading(true);
    const previousBookmarked = bookmarked;

    setBookmarked(!bookmarked);

    try {
      if (bookmarked) {
        await tweetService.unbookmarkTweet(tweet.id);
        toast({
          title: "Removed from bookmarks",
          description: "Tweet removed from your bookmarks",
        });
      } else {
        await tweetService.bookmarkTweet(tweet.id);
        toast({
          title: "Bookmarked",
          description: "Tweet added to your bookmarks",
        });
      }
    } catch (error) {
      setBookmarked(previousBookmarked);
      toast({
        title: "Error",
        description: "Failed to update bookmark status",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

 
  if (isDeleted) {
    return (
      <motion.div
        initial={{ opacity: 1, height: "auto" }}
        animate={{ opacity: 0, height: 0 }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.3 }}
        className="border-b border-border overflow-hidden"
      >
        <div className="p-4 text-center text-muted-foreground">
          <p className="text-sm">Tweet deleted</p>
        </div>
      </motion.div>
    );
  }

  return (
    <>
      <motion.article
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-border p-4 hover:bg-muted/50 transition-colors cursor-pointer"
      >
      <div className="flex gap-3">
        <Avatar className="w-12 h-12">
          <AvatarImage src={tweet.author?.profile_image_url} />
          <AvatarFallback>
            {tweet.author?.first_name?.[0] ||
              tweet.author?.username?.[0] ||
              "U"}
          </AvatarFallback>
        </Avatar>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-bold hover:underline">
              {tweet.author?.first_name || "Unknown"}
            </span>
            <span className="text-muted-foreground">
              @{tweet.author?.username || "unknown"}
            </span>
            <span className="text-muted-foreground">·</span>
            <span className="text-muted-foreground text-sm">
              {tweet.created_at
                ? (() => {
                    try {
                      const date = new Date(tweet.created_at);
                      return isNaN(date.getTime())
                        ? "Just now"
                        : formatDistanceToNow(date, { addSuffix: true });
                    } catch {
                      return "Just now";
                    }
                  })()
                : "Just now"}
            </span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="ml-auto h-8 w-8"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                {isOwnTweet ? (
                  <>
                    <DropdownMenuItem
                      className="text-destructive focus:text-destructive cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteClick();
                      }}
                      disabled={isDeleting}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      {isDeleting ? "Deleting..." : "Delete Tweet"}
                    </DropdownMenuItem>
                  </>
                ) : (
                  <>
                    <DropdownMenuItem
                      className="cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowReportDialog(true);
                      }}
                    >
                      <Flag className="w-4 h-4 mr-2" />
                      Report Tweet
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <p className="mb-3 whitespace-pre-wrap break-words">
            {tweet.content}
          </p>

          {tweet.media && tweet.media.length > 0 && (
            <div className="mb-3 rounded-2xl overflow-hidden border border-border">
              <img
                src={tweet.media[0].file_url}
                alt={tweet.media[0].alt_text || "Tweet media"}
                className="w-full object-cover max-h-96"
              />
            </div>
          )}

          <div className="flex items-center justify-between max-w-md">
            {/* Comment Button - Always visible */}
            <Button
              variant="ghost"
              size="sm"
              className={`gap-2 ${
                showReplies ? "text-primary" : "hover:text-primary"
              } ${disableReplies ? "opacity-50 cursor-not-allowed" : ""}`}
              onClick={(e) => {
                e.stopPropagation();
                if (!disableReplies) {
                  setShowReplies(!showReplies);
                }
              }}
              disabled={disableReplies}
            >
              <MessageCircle className="w-4 h-4" />
              <span className="text-sm">{replyCount}</span>
            </Button>

            {/* Retweet Button - Only for original tweets (nestingLevel === 0) */}
            {nestingLevel === 0 && (
              <Button
                variant="ghost"
                size="sm"
                className={`gap-2 ${
                  retweeted ? "text-green-500" : "hover:text-green-500"
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleRetweet();
                }}
              >
                <Repeat2 className="w-4 h-4" />
                <span className="text-sm">{retweetsCount}</span>
              </Button>
            )}

            {/* Like Button - Always visible */}
            <Button
              variant="ghost"
              size="sm"
              className={`gap-2 ${
                liked ? "text-pink-500" : "hover:text-pink-500"
              }`}
              onClick={(e) => {
                e.stopPropagation();
                handleLike();
              }}
            >
              <Heart className={`w-4 h-4 ${liked ? "fill-current" : ""}`} />
              <span className="text-sm">{likesCount}</span>
            </Button>

            {/* Bookmark Button - Only for original tweets (nestingLevel === 0) */}
            {nestingLevel === 0 && (
              <Button
                variant="ghost"
                size="sm"
                className={`${
                  bookmarked ? "text-primary" : "hover:text-primary"
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleBookmark();
                }}
              >
                <Bookmark
                  className={`w-4 h-4 ${bookmarked ? "fill-current" : ""}`}
                />
              </Button>
            )}

            {/* {nestingLevel === 0 && (
              <Button variant="ghost" size="sm" className="hover:text-primary">
                <Share className="w-4 h-4" />
              </Button>
            )} */}
          </div>
        </div>
      </div>

      {/* Replies Section - Lazy Loaded */}
      <AnimatePresence>
        {showReplies && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Suspense
              fallback={
                <div className="p-8 text-center border-t border-border">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto text-muted-foreground" />
                  <p className="text-sm text-muted-foreground mt-2">
                    Loading replies...
                  </p>
                </div>
              }
            >
              <TweetReplies
                tweetId={tweet.id}
                initialReplyCount={replyCount}
                nestingLevel={nestingLevel}
              />
            </Suspense>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent onClick={(e) => e.stopPropagation()}>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Tweet?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete your tweet
              and remove it from our servers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleDeleteCancel} disabled={isDeleting}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Report Dialog */}
      <ReportDialog
        isOpen={showReportDialog}
        onClose={() => setShowReportDialog(false)}
        contentType="tweet"
        objectId={tweet.id}
        objectDescription={tweet.content.substring(0, 100)}
      />
    </>
  );
};

export default TweetCard;
