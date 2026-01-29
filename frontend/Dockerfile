# ===========================================
# Flow Forecaster - Frontend Dockerfile
# Multi-stage build for production
# ===========================================

# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Build for production
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-/api}

RUN npm run build

# Stage 2: Production with Nginx
FROM nginx:alpine as production

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
