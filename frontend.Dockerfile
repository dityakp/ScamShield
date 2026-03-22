FROM nginx:alpine

# Copy the custom Nginx reverse proxy configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Copy all the frontend assets (html, css, js, images)
COPY ./assets /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
