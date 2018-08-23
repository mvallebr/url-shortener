# url-shortener

This is just an url-shortener service written using python and cassandra. It accepts POST requests to short an URL and a
GET request to retrieve the original one.

## Example usage

1. `GET www.helloworld.com` -> `hello world`
2. `POST www.your_service.com/shorten_url`
body:
```json
{
"url": "www.helloworld.com"
}
```
response body:
```json
{
"shortened_url": 'http://www.your_service.com/ouoYFY48'
}
```
3. `GET http://www.your_service.com/AQE=` -> `hello world`
 
## Running and testing

See [HACKING.md](HACKING.md) to instructions on how to develop, contribute, etc.  
 
## Details on the solution


### ID generation 

The main problem on building an url shortener that scales is the id generation. It's important to generate an unique ID
across all nodes in the cluster running this rest service. A naive approach would be trying to use database sequence and call the sequence every time a new URL is inserted (shortened). This works, as the DB serves as a central repository of IDs, but it adds a lot of latency to add each request and has a single point of failure - the DB. One advantage of this model, though, is the ability of generating really short urls, as IDs would start from 0. 

Another approach would be generating an UUID type 1, which includes the machine mac address and time, so ids would be unique on the database. This also works, but an UUID is too long for an url shortener, it would be something like `http://host/e0b52fce-a702-11e8-98d0-529269fb1459` - too long for one wanting a short URL.

The approach implemented in this project uses a combination of both solutions to get the better of both words. This Flask service was implemented taking into account no threads would be used when configuring it on wsgi or gunicorn, only processes. This removes the concerns about concurrency within one process, allow us to specify 1 different INSTANCE_ID on the flask config per process per host. The INSTANCE_ID must be unique across all nodes in the cluster and assigning this would be very environment dependant, so as far as this project is concerned the INSTANCE_ID is just a flask app configuration. 

The INSTANCE_ID is supposed to have at most 1 byte, meaning it would be a number between 0 and 255. It could be easily changed to 2 bytes, greatly increasing the total number of hosts, if desired. 

The short URLs then are generated by concatenating the 1 byte INSTANCE_ID with the CURRENT_ID for that instance. Every process keeps in memory a value of CURRENT_ID and increments it on every request. On every increment, the new value is sent to Cassandra, updating the column family `url_shortener.instance_seq`. As a result, many requests will be sent to Cassandra per second, but Cassandra is exactly optimized for fast writes, compacting data when writing to disk and allowing us to tune the eventual consistence, if needed. 

If the process is restarted, the current_id for that INSTANCE_ID is just read from Cassandra. 

The writes to `instance_seq` could be even more optimized, we could write 100 IDs in advance (i. e. if current_id = 100, we would write 200) and run the risk of losing 100 ids if the server crashes. Then we would be able to write only every 100 requests. This is optimization though and wasn't implemented in this repo. 

### Representing the ID in the URL

For the first request on instance 1, instance id would be 1 and current id would be 1 as well, meaning the resultant short_id would be 257 (or '0b100000001'). This is just 2 bytes long, but we must represent it on an URL using only URL valid chars, as we can't use the binary value. 

To minimize the space taken in the URL, this implementation used Base64. So the value of 257 would be converted to base 64 and would become `AQE=`, which is the representation in the URL.  Maybe this could be even more optimized, but for this implementation it was considered good enough.

### URL Validation

URL rules are defined by rfc 3986, so rfc3986 python library was used to validate the URLs. 
Besides the validation, it's possible to perform some auto fixes in the URLs, like automatically URL Encode some parts when needed, but this wasn't done in this implementation. The only auto fix implemented was automatically adding a default protocol, if one hasn't been specified in the original URL. 

Also, only specific protocols are allowed, in special FTP, HTTP and HTTPS. FILE, for instance, or any other, is blocked. This could be changed according to specific needs and requirements based on use cases. 

Local URLs like 'localhost' are allowed though. This could also be easily changed in `url_logic` module, but no check is performed regarding that. 

























