import { useState, useEffect } from 'react';
import { Plus, Search } from 'lucide-react';
import { Community, communityService } from '@/services/communityService';
import CommunityCard from '@/components/community/CommunityCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Communities = () => {
  const [allCommunities, setAllCommunities] = useState<Community[]>([]);
  const [myCommunities, setMyCommunities] = useState<Community[]>([]);
  const [discoverCommunities, setDiscoverCommunities] = useState<Community[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Community[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAllCommunities();
  }, []);

  const fetchAllCommunities = async () => {
    try {
      setIsLoading(true);
      const response = await communityService.getCommunities();
      setAllCommunities(response.results);
    } catch (error) {
      console.error('Failed to fetch communities:', error);
      toast({
        title: 'Error',
        description: 'Failed to load communities',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMyCommunities = async () => {
    try {
      setIsLoading(true);
      const response = await communityService.getMyCommunities();
      setMyCommunities(response.results);
    } catch (error) {
      console.error('Failed to fetch my communities:', error);
      toast({
        title: 'Error',
        description: 'Failed to load your communities',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDiscoverCommunities = async () => {
    try {
      setIsLoading(true);
      const response = await communityService.discoverCommunities();
      setDiscoverCommunities(response.results);
    } catch (error) {
      console.error('Failed to fetch discover communities:', error);
      toast({
        title: 'Error',
        description: 'Failed to load discover communities',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setIsSearching(true);
      const response = await communityService.searchCommunities(query);
      setSearchResults(response.results);
    } catch (error) {
      console.error('Failed to search communities:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleJoinCommunity = async (communityId: number) => {
    try {
      await communityService.joinCommunity(communityId);
      
      
      const updateCommunity = (communities: Community[]) =>
        communities.map(c =>
          c.id === communityId
            ? { ...c, is_member: true, members_count: c.members_count + 1 }
            : c
        );

      setAllCommunities(updateCommunity);
      setMyCommunities(updateCommunity);
      setDiscoverCommunities(updateCommunity);
      setSearchResults(updateCommunity);

      toast({
        title: 'Success',
        description: 'Joined community successfully',
      });
    } catch (error: any) {
      console.error('Failed to join community:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to join community',
        variant: 'destructive',
      });
    }
  };

  const handleLeaveCommunity = async (communityId: number) => {
    try {
      await communityService.leaveCommunity(communityId);
      
      // Update the community in all lists
      const updateCommunity = (communities: Community[]) =>
        communities.map(c =>
          c.id === communityId
            ? { ...c, is_member: false, members_count: c.members_count - 1 }
            : c
        );

      setAllCommunities(updateCommunity);
      setMyCommunities(prev => prev.filter(c => c.id !== communityId));
      setDiscoverCommunities(updateCommunity);
      setSearchResults(updateCommunity);

      toast({
        title: 'Success',
        description: 'Left community successfully',
      });
    } catch (error: any) {
      console.error('Failed to leave community:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to leave community',
        variant: 'destructive',
      });
    }
  };

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    if (value === 'my' && myCommunities.length === 0) {
      fetchMyCommunities();
    } else if (value === 'discover' && discoverCommunities.length === 0) {
      fetchDiscoverCommunities();
    }
  };

  const renderCommunities = (communities: Community[]) => {
    if (isLoading) {
      return (
        <div className="p-8 text-center text-muted-foreground">
          Loading communities...
        </div>
      );
    }

    if (!communities || communities.length === 0) {
      
      return (
        <div className="p-8 text-center text-muted-foreground">
          <p>No communities found</p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
        {communities.map(community => (
          <CommunityCard
            key={community.id}
            community={community}
            onJoin={handleJoinCommunity}
            onLeave={handleLeaveCommunity}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="flex-1 border-r border-border">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Communities</h1>
          <Button onClick={() => navigate('/communities/create')} className="gap-2">
            <Plus className="w-4 h-4" />
            Create
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search communities..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </header>

      {/* Search Results */}
      {searchQuery && (
        <div className="border-b border-border">
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4">
              Search Results {isSearching && '(searching...)'}
            </h2>
            {renderCommunities(searchResults)}
          </div>
        </div>
      )}

      {/* Tabs */}
      {!searchQuery && (
        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
          <TabsList className="w-full h-14 rounded-none bg-transparent border-b border-border">
            <TabsTrigger
              value="all"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              All
            </TabsTrigger>
            <TabsTrigger
              value="my"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              My Communities
            </TabsTrigger>
            <TabsTrigger
              value="discover"
              className="flex-1 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              Discover
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-0">
            {renderCommunities(allCommunities)}
          </TabsContent>

          <TabsContent value="my" className="mt-0">
            {renderCommunities(myCommunities)}
          </TabsContent>

          <TabsContent value="discover" className="mt-0">
            {renderCommunities(discoverCommunities)}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default Communities;
