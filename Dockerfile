FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Build frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Python stage
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including nginx
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend
COPY --from=frontend-builder /frontend/dist /var/www/html

# Copy nginx config
RUN rm /etc/nginx/sites-enabled/default
COPY <<EOF /etc/nginx/sites-available/app
server {
    listen 7777;
    server_name localhost;
    root /var/www/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml;

    location /api {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/

# Copy supervisor config
COPY <<EOF /etc/supervisor/conf.d/app.conf
[supervisord]
nodaemon=true
user=root

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:uvicorn]
command=uvicorn app.main:app --host 127.0.0.1 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

EXPOSE 7777

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]

