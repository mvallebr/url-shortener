import logging
import pytest
from rfc3986.exceptions import RFC3986Exception
from urllib.parse import quote

from rest_api.id_cache import concatenate_instance
from rest_api.url_logic import encode_short_id, decode_short_id, enforce_scheme, validate_url

concatenate_instance_data = [
    (1, 1, '0b100000001',),
    (2, 1, '0b100000010',),
    (1, 2, '0b1000000001',),
]


@pytest.mark.parametrize(argnames="instance_id, current_id, expected_bin_repr", argvalues=concatenate_instance_data)
def test_concatenate_instance(instance_id, current_id, expected_bin_repr):
    assert bin(concatenate_instance(instance_id=instance_id, current_id=current_id)) == expected_bin_repr


enc_dec_short_id_data = [
    (1, 1, "AQE=",),
    (1, 2, "AQI=",),
    (1, 3, "AQM=",),
]


@pytest.mark.parametrize(argnames="instance_id, current_id, short_id_str", argvalues=enc_dec_short_id_data)
def test_encode_decode_short_id(instance_id, current_id, short_id_str):
    assert encode_short_id(concatenate_instance(instance_id=instance_id, current_id=current_id)) == short_id_str
    assert decode_short_id(short_id_str) == concatenate_instance(instance_id=instance_id, current_id=current_id)


enforce_scheme_data = [
    ('www.google.com', 'http://www.google.com', 'http',),
    ('http://www.google.com', 'http://www.google.com', 'HTTPS',),
    ('ftp://www.google.com', 'ftp://www.google.com', 'http',),
    ('https://www.google.com', 'https://www.google.com', 'http',),
    ('abcd://www.google.com', 'abcd://www.google.com', 'http',),
]


@pytest.mark.parametrize(argnames="original_url, expected_url, default_scheme", argvalues=enforce_scheme_data)
def test_enforce_scheme(original_url, expected_url, default_scheme):
    assert enforce_scheme(url=original_url, default_scheme=default_scheme) == expected_url


validate_url_data = [
    ('www.google.com', False,),
    ('http://www.google.com', True,),
    ('ftp://www.google.com', True,),
    ('ftp://www.google.com/path/complex/123?with=parameters&and=more', True,),
    ('https://www.google.com', True,),
    ('abcd://www.google.com', False,),
    ('abcd', False,),
    ('http://', False,),
    ('https://localhost/', True,),
    ('https://localhost/path', True,),
    ('https://example.com/file[/as].html', False),
    ('https://example.com/file/{}'.format(quote('[/as].html')), True),
    ('www. google', False,),
    ('scheme:host:port:path:but_what?', False,),
    ('', False,),
]


@pytest.mark.parametrize(argnames="original_url, expected_valid", argvalues=validate_url_data)
def test_validate_url_data(original_url, expected_valid):
    is_valid = True
    try:
        validate_url(original_url)
    except RFC3986Exception as e:
        logging.info("Url seems invalid: {}", e)
        is_valid = False
    result_ok = is_valid == expected_valid
    if not result_ok:
        logging.error("url {} validation returned {} but should be {}".format(original_url, is_valid, expected_valid))
    assert result_ok
