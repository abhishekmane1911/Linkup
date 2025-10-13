# Linkup - Social Media Web Application

A modern, Twitter-like social media platform built with React, TypeScript, Tailwind CSS, and Framer Motion on the frontend.

![Linkup](https://img.shields.io/badge/React-18.3.1-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-blueviolet)

## ✨ Features

### Implemented in Frontend

- ✅ **User Authentication** - Login, Signup, Logout pages with JWT support
- ✅ **User Profiles** - Display name, username, bio, avatar, verification badge, follower/following counts
- ✅ **Tweet System** - Create, view tweets with character limit (280)
- ✅ **Interactive Tweet Cards** - Like, retweet, bookmark, share, reply buttons with animations
- ✅ **Home Feed** - "For You" and "Following" tabs
- ✅ **Notifications** - Like, retweet, follow, reply, mention notifications
- ✅ **Direct Messages** - Conversation list and messaging interface
- ✅ **Explore Page** - Search and trending topics
- ✅ **Settings Page** - Dark/light mode toggle, account settings
- ✅ **Responsive Design** - Mobile navigation bar, desktop sidebar
- ✅ **Smooth Animations** - Framer Motion transitions and micro-interactions
- ✅ **Beautiful UI** - Twitter-inspired design with custom color scheme

### Ready for Backend Integration

All components are designed with API integration patterns using Axios. Simply replace the mock data with your Flask API calls.

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- MySQL database (for backend)
- Python 3.9+ (for Flask backend)

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

The app will be available at `http://localhost:8080`

### Backend Setup

See **[FLASK_BACKEND_GUIDE.md](./FLASK_BACKEND_GUIDE.md)** for complete Flask backend integration instructions.

Quick start:
1. Set up your MySQL database with the provided schema
2. Create Flask backend following the guide
3. Update API URLs in frontend code
4. Run Flask backend on port 5000
5. Frontend will connect automatically

## 🎨 Design System

### Color Scheme

**Light Mode:**
- Background: Clean white
- Primary: Twitter Blue (#1DA1F2)
- Accent: Purple (#8B5CF6)

**Dark Mode (Default):**
- Background: Near-black (#151A23)
- Primary: Twitter Blue
- Accent: Purple
- Cards: Dark gray with subtle elevation

### Typography

- System fonts for optimal performance
- Font weights: 400 (regular), 500 (medium), 700 (bold)

### Components

All UI components are built with **shadcn/ui** and fully customizable:
- Buttons with multiple variants
- Cards with hover effects
- Avatars with fallbacks
- Tabs, Inputs, Dialogs, etc.

## 📁 Project Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Layout.tsx          # Protected route wrapper
│   │   ├── Sidebar.tsx         # Desktop navigation
│   │   └── MobileNav.tsx       # Mobile bottom navigation
│   ├── tweet/
│   │   ├── TweetCard.tsx       # Individual tweet display
│   │   └── TweetComposer.tsx   # Tweet creation form
│   └── ui/                     # shadcn UI components
├── contexts/
│   └── AuthContext.tsx         # Authentication state management
├── pages/
│   ├── Home.tsx                # Main feed
│   ├── Login.tsx               # Login page
│   ├── Signup.tsx              # Registration page
│   ├── Profile.tsx             # User profile
│   ├── Notifications.tsx       # Notifications feed
│   ├── Messages.tsx            # Direct messages
│   ├── Explore.tsx             # Search & trending
│   └── Settings.tsx            # App settings
├── types/
│   └── index.ts                # TypeScript interfaces
└── App.tsx                     # Main app with routing
```

## 🔌 API Integration Points

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Tweets
- `GET /api/tweets/feed` - Get timeline
- `POST /api/tweets` - Create tweet
- `DELETE /api/tweets/:id` - Delete tweet
- `POST /api/tweets/:id/like` - Like/unlike
- `POST /api/tweets/:id/retweet` - Retweet

### Users
- `GET /api/users/:username` - Get profile
- `PUT /api/users/:username` - Update profile
- `POST /api/users/:username/follow` - Follow/unfollow
- `GET /api/users/:username/followers` - Get followers
- `GET /api/users/:username/following` - Get following

### Complete API documentation in [FLASK_BACKEND_GUIDE.md](./FLASK_BACKEND_GUIDE.md)

## 🗄️ Database Schema

Your MySQL schema includes:

- **User** - User accounts and profiles
- **Tweet** - User posts with threading support
- **Follows** - Follow relationships
- **Likes** - Tweet likes
- **Retweets** - Tweet shares
- **Bookmarks** - Saved tweets
- **Media** - Images/videos/gifs
- **Hashtag** - Trending topics
- **Conversation** - DM conversations
- **Direct_Message** - Private messages
- **Lists** - User-created lists
- **Report** - Content moderation

## 🎯 Usage

### Default Behavior

- App starts in **dark mode** (toggle in Settings)
- Must login to access main features
- Demo credentials work for testing (see AuthContext.tsx)
- All animations are enabled by default

### Creating a Tweet

1. Click "Tweet" button in sidebar (or bottom-right on mobile)
2. Type your message (max 280 characters)
3. Optionally add media (placeholder - connect backend)
4. Click "Tweet" to post

### Viewing Profiles

1. Click on any user's name or avatar
2. View their tweets, replies, media, and likes
3. Click "Follow" to follow them

### Switching Themes

1. Go to Settings page
2. Toggle "Dark Mode" switch
3. Theme preference is saved in localStorage

## 🔒 Security Features

- JWT-based authentication
- Password hashing (backend)
- Protected routes
- XSS prevention
- CSRF tokens (to be implemented in backend)

## 🚧 Remaining Tasks

### Backend Implementation
1. Create Flask backend following the guide
2. Implement all API endpoints
3. Connect to MySQL database
4. Add file upload support for media
5. Implement WebSocket for real-time features

### Optional Enhancements
1. Image compression before upload
2. Infinite scroll pagination
3. Real-time notifications
4. Post analytics
5. Email verification
6. Password reset
7. Two-factor authentication

## 📚 Technologies Used

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **React Router** - Navigation
- **Axios** - HTTP client
- **shadcn/ui** - Component library
- **date-fns** - Date formatting
- **Lucide React** - Icons

### Backend (To Implement)
- **Flask** - Python web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **MySQL** - Database
- **Flask-CORS** - CORS handling

## 🤝 Contributing

This is a database project. To extend:

1. Add new features to frontend
2. Implement corresponding backend endpoints
3. Update the database schema if needed
4. Test thoroughly

## 📝 Notes

- All TODO comments in code mark where Flask API calls should be added
- Mock data is used for demonstration purposes
- Avatar images use DiceBear API for placeholders
- Dark mode is default and recommended for best experience

## 🎓 Learning Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

## 📄 License

This is a university database project.

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
