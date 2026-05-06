# Docker Setup Guide

## Project Structure
```
Dockerfile              # Multi-stage production-ready Docker image
docker-compose.yml      # Full stack with Django, PostgreSQL, and Nginx
nginx.conf             # Nginx configuration for reverse proxy
.dockerignore          # Files to exclude from Docker build
.env.example           # Template for environment variables
requirements.txt       # Python dependencies with gunicorn & psycopg2
```

## Quick Start

### 1. **Clone and Setup**
```bash
git clone <repo>
cd Ecommerce
cp .env.example .env
```

### 2. **Configure .env**
Edit `.env` and add your credentials:
```
SECRET_KEY=your-random-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
DB_PASSWORD=strong-db-password
```

### 3. **Build and Run**
```bash
docker-compose up -d
```

### 4. **Initialize Database**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

## Accessing the App
- **Django App**: http://localhost:8000
- **Through Nginx**: http://localhost
- **Admin Panel**: http://localhost/admin

## Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| Web (Django) | ecommerce-app | 8000 | Django application with Gunicorn |
| Database | ecommerce-db | 5432 | PostgreSQL database |
| Reverse Proxy | ecommerce-nginx | 80 | Nginx reverse proxy for static/media |

## Common Commands

### View logs
```bash
docker-compose logs -f web        # Django logs
docker-compose logs -f db         # Database logs
docker-compose logs -f nginx      # Nginx logs
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Run migrations
```bash
docker-compose exec web python manage.py migrate
```

### Stop all services
```bash
docker-compose down
```

### Remove everything (including volumes)
```bash
docker-compose down -v
```

## Docker Architecture

### Multi-Stage Dockerfile
- **Stage 1 (Builder)**: Installs build dependencies, compiles Python packages
- **Stage 2 (Runtime)**: Minimal image with only runtime dependencies
- **Result**: Smaller final image (~400MB vs ~800MB)

### Key Features
✅ Non-root user for security  
✅ Health checks for container orchestration  
✅ Static file collection  
✅ Gunicorn for production WSGI  
✅ Environment variable configuration  
✅ PostgreSQL support  
✅ Nginx reverse proxy  
✅ Volume management for persistence  

## Environment Configuration

### For Development
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### For Production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=<generate-strong-key>
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Database Migration Path

### From SQLite to PostgreSQL
The Docker setup uses PostgreSQL by default. To migrate existing SQLite data:

```bash
# 1. Backup current SQLite
cp db.sqlite3 db.sqlite3.backup

# 2. Export data (on local machine)
python manage.py dumpdata > data.json

# 3. Copy to container and load
docker-compose cp data.json web:/app/
docker-compose exec web python manage.py loaddata data.json
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml or:
docker-compose down
```

### Database Connection Error
```bash
# Check PostgreSQL service
docker-compose logs db

# Recreate container
docker-compose down db
docker volume rm ecommerce_postgres_data
docker-compose up -d
```

### Static files not loading
```bash
docker-compose exec web python manage.py collectstatic --noinput --clear
```

### Permission denied errors
```bash
docker-compose exec web chown -R appuser:appuser /app
```

## Performance Tuning

### Increase Workers (for high traffic)
Edit `docker-compose.yml`:
```yaml
command: gunicorn --bind 0.0.0.0:8000 --workers 8 ecommerce.wsgi:application
```

### Enable Database Connection Pooling
Add to requirements.txt: `django-db-geventpool`

### Use Redis for Caching (Optional)
Add to docker-compose.yml and install `django-redis`

## Production Deployment

For production on cloud platforms (AWS, DigitalOcean, etc.):

1. Update `ALLOWED_HOSTS` with your domain
2. Generate secure `SECRET_KEY`
3. Set `DEBUG=False`
4. Use environment-specific `.env` files
5. Enable HTTPS/SSL (use Let's Encrypt)
6. Set up backup strategy for PostgreSQL
7. Configure CDN for static files

## Security Checklist
- [ ] Generate new SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set strong DB_PASSWORD
- [ ] Enable HTTPS
- [ ] Configure CORS if needed
- [ ] Review environment variables
- [ ] Set proper file permissions
