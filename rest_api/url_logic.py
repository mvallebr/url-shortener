import base64


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
