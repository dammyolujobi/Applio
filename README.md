# Applio - Job Aggregator Platform

A comprehensive job aggregation web application built with Python and FastAPI that scrapes job listings from multiple sources including Nigerian job sites (Jobberman, MyJobMag), global platforms (Indeed, LinkedIn, ZipRecruiter, Google Jobs), and Apple Careers.

## Features

### Core Functionality
- **Multi-Source Job Scraping**: Aggregates jobs from Jobberman, MyJobMag, Indeed, LinkedIn, ZipRecruiter, Google Jobs, and Apple Careers
- **Advanced Filtering**: Filter by job type, experience level, salary range, company, and location
- **Sorting Options**: Sort by date, salary, or relevance
- **Pagination**: Efficient pagination to handle large datasets
- **Caching Layer**: Redis-backed caching for improved performance

### User Management
- **JWT Authentication**: Secure authentication with access and refresh tokens
- **User Profiles**: Complete profile management with skills, bio, and location
- **Password Management**: Secure password hashing and change functionality

### Job Management
- **Save/Favorite Jobs**: Bookmark interesting job opportunities
- **Job Alerts**: Get notified about new matching positions
- **Application Tracking**: Track your job applications through different stages
- **Search History**: View and manage your search history

### Additional Features
- **Rate Limiting**: Protection against abuse
- **User Activity Tracking**: Monitor user interactions
- **Error Recovery**: Graceful handling of scraper failures
- **CORS Configuration**: Properly configured for frontend integration

## API Endpoints

### Authentication
- `POST /users/register` - Register a new user
- `POST /users/login` - Login and get tokens
- `POST /users/refresh-token` - Refresh access token

### User Profile
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `POST /users/change-password` - Change password

### Jobs
- `POST /aggregate` - Search and aggregate jobs with filters
- `GET /jobs/{job_id}` - Get detailed job information

### Saved Jobs
- `POST /users/saved-jobs` - Save a job
- `GET /users/saved-jobs` - Get all saved jobs
- `DELETE /users/saved-jobs/{job_id}` - Remove saved job

### Job Alerts
- `POST /users/alerts` - Create job alert
- `GET /users/alerts` - Get all alerts
- `PUT /users/alerts/{alert_id}` - Update alert
- `DELETE /users/alerts/{alert_id}` - Delete alert

### Applications
- `POST /users/applications` - Track new application
- `GET /users/applications` - Get all applications
- `PUT /users/applications/{app_id}` - Update application status

### Search History
- `POST /users/search-history` - Log search
- `GET /users/search-history` - Get search history

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd applio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start MongoDB (if running locally):
```bash
mongod
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file with the following variables:

```env
JWT_SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
JWT_REFRESH_KEY=your-super-secret-refresh-key
CONNECTION_STRING=mongodb://localhost:27017
```

## Tech Stack

- **Backend**: FastAPI, Python
- **Database**: MongoDB
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Web Scraping**: BeautifulSoup, requests, python-jobspy
- **Rate Limiting**: slowapi
- **Validation**: Pydantic

## License

MIT License
