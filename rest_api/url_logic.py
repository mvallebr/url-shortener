import base64


# only the first byte of instance id is considered, which means we can have 256 max process in the cluster.
# If there is intention of increasing the number of machines, this mask has to be changed.
INSTANCE_ID_MASK = 255
INSTANCE_ID_NUM_BITS = 8


def concatenate_instance(instance_id: int, current_id: int) -> int:
    """
    The short url id reserves a fixed number of bytes for the instance and the remaining part is the current_id for the
    instance. The objective is to get a result url which is as short as possible.
    :param instance_id: instance id of this running process - this should come from config
    :param current_id: the current id for the instance
    :return: the concatenated id according to the rules above.
    """
    return (instance_id & INSTANCE_ID_MASK) + (current_id << INSTANCE_ID_NUM_BITS)

def encode_short_id(short_id: int) -> str:
    """
    Encodes a short id in the shortest way possible it can be represented in the url.
    :param short_id: int to be used on a short url
    :return: integer encoded to base 64
    """
    short_id_as_byte_array = short_id.to_bytes((short_id.bit_length() + 7) // 8, byteorder='little')
    return base64.b64encode(short_id_as_byte_array).decode("utf-8")


def decode_short_id(short_id_encoded: str) -> int:
    """
    Decodes a short id url representation to the integer that originated it
    :param short_id_encoded: base64 representation
    :return: original short id as integer
    """
    return int.from_bytes(base64.b64decode(short_id_encoded.encode("utf-8")), 'little')
