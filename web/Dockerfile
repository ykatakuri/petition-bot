FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./nginx.conf/nginx.conf /etc/nginx/conf.d/
COPY ./nginx.conf/bot.crt /etc/nginx/certs/
COPY ./nginx.conf/bot.key /etc/nginx/certs/
COPY . /usr/share/nginx/html/
