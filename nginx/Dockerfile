FROM nginx:1.19.7-alpine

# Add bash and openssl for certificate generation
RUN apk add --no-cache bash openssl

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Generate self-signed SSL certificate
RUN openssl req -newkey rsa:2048 -nodes -keyout /etc/nginx/ssl/server.key -x509 -days 365 -out /etc/nginx/ssl/server.crt -subj "/C=AU/ST=QLD/L=BNE/O=Babbler/OU=Babbler/CN=20.5.196.24"

# Set permissions for SSL files
RUN chmod 600 /etc/nginx/ssl/server.key && \
    chmod 644 /etc/nginx/ssl/server.crt && \
    chown nginx:nginx /etc/nginx/ssl/server.key /etc/nginx/ssl/server.crt

# Add nginx.conf to container
COPY --chown=nginx:nginx nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx start.sh /app/start.sh

# Set workdir
WORKDIR /app

# Permissions and nginx user for tightened security
RUN chown -R nginx:nginx /app && chmod -R 755 /app && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chmod -R 755 /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Create nginx.pid file and set permissions
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid

# Switch to nginx user
USER nginx

CMD ["nginx", "-g", "daemon off;"]
