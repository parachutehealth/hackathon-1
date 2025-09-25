FROM 211125529252.dkr.ecr.us-east-1.amazonaws.com/ruby:3.2.4-node-16.14.0

RUN apt-get update && apt-get install -y \
  chromium \
  chromium-driver

ADD myapp.rb /app

WORKDIR /app
RUN gem install sinatra rackup puma

ADD . /app

RUN ruby myapp.rb