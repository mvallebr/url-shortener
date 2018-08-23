from rest_api.id_cache import concatenate_instance
from rest_api.url_logic import encode_short_id, decode_short_id


def test_concatenate_instance():
    assert bin(concatenate_instance(instance_id=1, current_id=1)) == '0b100000001'
    assert bin(concatenate_instance(instance_id=2, current_id=1)) == '0b100000010'
    assert bin(concatenate_instance(instance_id=1, current_id=2)) == '0b1000000001'


def test_encode_decode_short_id():
    assert encode_short_id(concatenate_instance(instance_id=1, current_id=1)) == "AQE="
    assert encode_short_id(concatenate_instance(instance_id=1, current_id=2)) == "AQI="
    assert encode_short_id(concatenate_instance(instance_id=1, current_id=3)) == "AQM="
    assert decode_short_id("AQE=") == concatenate_instance(instance_id=1, current_id=1)
    assert decode_short_id("AQI=") == concatenate_instance(instance_id=1, current_id=2)
    assert decode_short_id("AQM=") == concatenate_instance(instance_id=1, current_id=3)
