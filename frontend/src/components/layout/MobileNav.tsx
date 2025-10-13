import { Link, useLocation } from 'react-router-dom';
import { Home, Search, Bell, Mail, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const MobileNav = () => {
  const location = useLocation();
  const { user } = useAuth();

  const navItems = [
    { icon: Home, label: 'Home', path: '/' },
    { icon: Search, label: 'Explore', path: '/explore' },
    { icon: Bell, label: 'Notifications', path: '/notifications' },
    { icon: Mail, label: 'Messages', path: '/messages' },
    { icon: User, label: 'Profile', path: `/profile/${user?.username}` },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-card border-t border-border z-50">
      <div className="flex justify-around items-center h-16">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="flex flex-col items-center justify-center flex-1 h-full"
          >
            <item.icon
              className={`w-6 h-6 ${
                isActive(item.path) ? 'text-primary' : 'text-muted-foreground'
              }`}
            />
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default MobileNav;
