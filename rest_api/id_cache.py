"""
This module serves just as a "singleton" for the current id being hold in this process.
Please remember that this application should not be configured with multiple threads on wsgi or gunicorn, only with
multiple processes.  Even knowing Python has GIL, we shouldn't design applications counting on GIL - some interpreters
try to overcome GIL in some cases, for example.

Every process serving the flask app should have a different instance ID passed as a configuration parameter. At
application start up, the process read the current id from a table in Cassandra.

Every time a request comes, the id is incremented and concatenated with the instance id it becomes the id of the
generated url. The incremented id is also saved back to Cassandra on every request.
Cassandra will save a lot of modifications in memory before flushing to disk, so it won't actually create a huge table
on disk with many versions, most compacting will happen in memory, before the flush.
"""
from flask import current_app

from rest_api import db
from rest_api.url_logic import concatenate_instance

cache = {}


def get_a_new_id() -> int:
    """
    This reads the current id either from cache or cassandra, and saves the incremented id back to cassandra.
    :return: the incremented id already concatenated with the instance
    """
    instance_id = current_app.config['INSTANCE_ID']
    # to make these 2 lines thread safe, we could use a lock and the with keyword (with some_lock:).
    # By design, I am not doing it, as locks also incur in overhead and this was designed to be lock free.
    current_id = cache.get("id", db.get_current_id(instance_id)) + 1
    cache["id"] = current_id

    db.upsert_current_id(instance_id, current_id)
    return concatenate_instance(instance_id, current_id)
