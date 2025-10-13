# Linkup Backend

Django REST API backend for the Linkup social media platform.

## Setup

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up MySQL database:

   - Open MySQL Workbench and connect to your MySQL server
   - Create database: `CREATE DATABASE linkup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
   - Or run: `python create_database.py` (after step 4)

4. Copy environment file and configure:

```bash
cp .env.example .env
# Edit .env with your MySQL credentials (DB_PASSWORD, etc.)
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create superuser (optional):

```bash
python manage.py createsuperuser
```

7. Run development server:

```bash
python manage.py runserver
```

## Project Structure

```
backend/
├── apps/                    # Django applications
│   ├── authentication/     # User authentication
│   ├── users/              # User management
│   ├── tweets/             # Tweet functionality
│   ├── interactions/       # Social interactions (likes, retweets, etc.)
│   ├── messaging/          # Direct messaging
│   ├── communities/        # Community features
│   ├── moderation/         # Content moderation
│   └── common/             # Shared utilities
├── linkup_backend/         # Main project configuration
│   ├── settings/           # Settings modules
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings
│   └── urls.py            # Main URL configuration
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## API Endpoints

The API will be available at `/api/v1/` with the following main endpoints:

- `/api/v1/auth/` - Authentication endpoints
- `/api/v1/users/` - User management
- `/api/v1/tweets/` - Tweet operations
- `/api/v1/interactions/` - Social interactions
- `/api/v1/messaging/` - Direct messaging
- `/api/v1/communities/` - Community features
- `/api/v1/moderation/` - Content moderation

## Development

- The project uses Django REST Framework for API development
- JWT authentication is configured for secure API access
- CORS is configured for frontend integration
- Media files are handled for user uploads

## Next Steps

1. Implement authentication system (Task 2)
2. Create user models and management (Task 2)
3. Build tweet functionality (Task 3)
4. Add social interactions (Task 4)
5. Implement remaining features as per the task list
