from cassandra.cluster import Cluster
from flask import Flask

app = Flask(__name__)

cluster = Cluster(['cassandra'])
session = cluster.connect('url_shortener')


def insert_short_url():
    session.execute(
        """
        INSERT INTO url_alias (short_id, original_url)
        VALUES (%s, %s)
        """,
        (42, "http://example.com/example/folder/file")
    )


@app.route('/')
def hello():
    insert_short_url()
    return "Hello World! "


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
