FROM nginx:stable-alpine

COPY ./nginx.conf /etc/nginx/nginx.conf
RUN mkdir /static
COPY ./index.html /static
