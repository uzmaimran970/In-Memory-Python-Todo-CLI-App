# Dockerfile for Frontend Example Application
# Builds a simple static website for the Local K8s AI Ops demo

FROM nginx:alpine

# Copy the example frontend application to nginx html directory
COPY index.html /usr/share/nginx/html/

# Copy custom nginx configuration if needed
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]