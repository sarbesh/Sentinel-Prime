FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /downloads && chown -R nginx:nginx /downloads

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
