
    require 'sinatra'

    set :port, 3000
    get '/' do
      'hack1 get root'
    end

    get 'health' do
      'health ok'
    end