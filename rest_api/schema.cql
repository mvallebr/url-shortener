DROP KEYSPACE IF EXISTS url_shortener;
CREATE KEYSPACE url_shortener WITH REPLICATION = {'class' : 'SimpleStrategy','replication_factor' : 1};
CREATE TABLE url_shortener.url_alias (short_id int, original_url text, PRIMARY KEY (short_id));