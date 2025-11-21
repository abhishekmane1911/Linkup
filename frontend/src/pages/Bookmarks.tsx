import { tweetService } from "@/services/tweetService";
import { useEffect, useState } from 'react';
import { Tweet } from "@/types";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from '@/contexts/AuthContext';
import TweetCard from '@/components/tweet/TweetCard';
import { Bookmark } from 'lucide-react';

interface BookmarkItem {
  id: number;
  tweet: Tweet;
  created_at: string;
}

const Bookmarks = () => {
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user: currentUser } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (currentUser) {
      fetchBookmarkedTweets();
    }
  }, [currentUser]);

  const fetchBookmarkedTweets = async () => {
    try {
      setIsLoading(true);
      const response = await tweetService.getBookmarkedTweets();
      console.log('Bookmarks response:', response);
      
      // The API returns { bookmarks: [...], count: number }
      if (response.bookmarks) {
        console.log('Individual bookmark:', response.bookmarks[0]);
        console.log('Tweet media:', response.bookmarks[0]?.tweet?.media);
        
        // Filter out bookmarks without proper tweet/author data and ensure is_bookmarked is true
        const validBookmarks = response.bookmarks
          .filter((bookmark: BookmarkItem) => bookmark.tweet && bookmark.tweet.author)
          .map((bookmark: BookmarkItem) => {
            const updatedTweet = {
              ...bookmark.tweet,
              is_bookmarked: true, // Ensure bookmark icon is filled since we're on the bookmarks page
              media: bookmark.tweet.media || [] // Ensure media array exists
            };
            console.log('Updated tweet media:', updatedTweet.media);
            return {
              ...bookmark,
              tweet: updatedTweet
            };
          });
        setBookmarks(validBookmarks);
      } else {
        // Fallback if the response structure is different
        console.log('No bookmarks in response, full response:', response);
        setBookmarks([]);
      }
    } catch (error: any) {
      console.error("Failed to fetch bookmarked tweets:", error);
      toast({
        title: "Error",
        description: "Failed to load bookmarked tweets",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentUser) {
    return (
      <div className="flex-1 p-8">
        <div className="text-center">
          <p className="text-muted-foreground">Please log in to view your bookmarks.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 border-r border-border">
      <header className="sticky top-0 bg-background/80 backdrop-blur-md border-b border-border p-4 z-10">
        <div className="flex items-center gap-3">
          <Bookmark className="w-6 h-6" />
          <div>
            <h1 className="text-xl font-bold">Bookmarks</h1>
            <p className="text-sm text-muted-foreground">
              {bookmarks.length} {bookmarks.length === 1 ? 'tweet' : 'tweets'}
            </p>
          </div>
        </div>
      </header>

      <div className="pb-20">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="text-muted-foreground mt-4">Loading bookmarks...</p>
          </div>
        ) : bookmarks.length === 0 ? (
          <div className="p-8 text-center">
            <Bookmark className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold mb-2">No bookmarks yet</h3>
            <p className="text-muted-foreground">
              When you bookmark tweets, they'll show up here.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {bookmarks.map((bookmark) => (
              <TweetCard
                key={bookmark.id}
                tweet={bookmark.tweet}

              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};



export default Bookmarks;
