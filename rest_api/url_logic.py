import base64

from rfc3986 import validators, uri_reference

from rfc3986.exceptions import ValidationError

# only the first byte of instance id is considered, which means we can have 256 max process in the cluster.
# If there is intention of increasing the number of machines, this mask has to be changed.

INSTANCE_ID_MASK = 255
INSTANCE_ID_NUM_BITS = 8

VALID_SCHEMES = ('http', 'ftp', 'https')
validator = validators.Validator().allow_schemes(*VALID_SCHEMES).forbid_use_of_password().require_presence_of(
    'scheme', 'host').check_validity_of(*validators.Validator.COMPONENT_NAMES)
scheme_presence_validator = validators.Validator().require_presence_of('scheme')


def validate_url(url: str):
    """
    Validate the url against several checks and raises an exception in case of validation failure
    :param url: a string with the url to be validated
    :return: None
    """
    validator.validate(uri_reference(url))


def enforce_scheme(url: str, default_scheme: str) -> str:
    """
    Makes sure the input url has a scheme. Otherise, add a default one.
    :param url: the input url with or without a scheme.
    :param default_scheme: default scheme to be added
    :return: an url with a default scheme or the original one
    """
    try:
        scheme_presence_validator.validate(uri_reference(url))
        return url
    except ValidationError:
        return "{}://{}".format(default_scheme, url)


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
    Encodes a short id in the shortest way possible (ideally) it can be represented in the url.
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
