import { Link, useLocation } from 'react-router-dom';
import { Home, Search, Bell, Mail, User, Settings, LogOut, Feather, Bookmark, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { useNotificationCount } from '@/hooks/useNotifications';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { unreadCount } = useNotificationCount();

  const navItems = [
    { icon: Home, label: 'Home', path: '/' },
    { icon: Search, label: 'Explore', path: '/explore' },
    { icon: Bell, label: 'Notifications', path: '/notifications' },
    { icon: Mail, label: 'Messages', path: '/messages' },
    { icon: Users, label: 'Communities', path: '/communities' },
    { icon: Bookmark, label: 'Bookmarks', path: '/bookmarks' },
    { icon: User, label: 'Profile', path: `/profile/${user?.username}` },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <motion.aside
      initial={{ x: -40, opacity: 0 }}
      animate={{ x: -20, opacity: 1 }}
      className="sticky top-0 h-screen w-48 border-r border-border p-4 hidden lg:flex flex-col"
    >
      <div className="flex items-center gap-2 mb-8 px-3">
        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
          <Feather className="w-6 h-6 text-primary-foreground" />
        </div>
        <h1 className="text-2xl font-bold ">Linkup</h1>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <Link key={item.path} to={item.path}>
            <Button
              variant={isActive(item.path) ? 'secondary' : 'ghost'}
              className="w-full justify-start gap-4 text-lg relative"
            >
              <item.icon className="w-6 h-6" />
              <span className="font-medium">{item.label}</span>
              {item.label === 'Notifications' && unreadCount > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-5 min-w-5 flex items-center justify-center px-1"
                >
                  {unreadCount > 99 ? '99+' : unreadCount}
                </Badge>
              )}
            </Button>
          </Link>
        ))}
      </nav>

      <div className="space-y-2">
        

        <Button
          variant="ghost"
          onClick={logout}
          className="w-full justify-start gap-4 text-lg text-muted-foreground hover:text-foreground hover:bg-red-500"
        >
          <LogOut className="w-6 h-6" />
          <span className="font-medium">Logout</span>
        </Button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
