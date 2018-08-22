# Hacking 

This project uses docker to provide a quick to set up environment and as an easy way of running tests. 

To run all tests for the project just run on the root folder of the project:

```bash
docker-compose build && docker-compose run -e FLASK_APP=rest_api tests pytest
```
 
To start the app so you can access the endpoint from your machine, run instead:

```bash
docker-compose up
```

And then point your browser to `http://localhost:5000/` to access the app. You can use this to call the app using curl.
For instance:

```bash
curl -d '{"url": "www.helloworld.com"}' -H "Content-Type: application/json" -X POST http://localhost:5000/shorten_url
``` 