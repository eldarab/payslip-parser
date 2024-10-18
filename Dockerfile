FROM nginx:alpine
COPY site/ /usr/share/nginx/html
COPY nginx-default.conf /etc/nginx/conf.d/default.conf