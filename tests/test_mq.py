import pytest
import struct
from BrainStorm.mq import create_mq_connection

_TOPIC = "abcd"

def test_create_valid_rabbit():
    con = create_mq_connection("rabbitmq://127.0.0.1:8080/",_TOPIC)
    assert con != None


def test_create_invalid_rabbit_no_port():
    with pytest.raises(ValueError):
        con = create_mq_connection("rabbitmq://127.0.0.1/",_TOPIC)


def test_create_invalid_rabbit_no_numer_port():
    with pytest.raises(ValueError):
        con = create_mq_connection("rabbitmq://127.0.0.1:abcd/",_TOPIC)


def test_create_invalid_scheme():
    with pytest.raises(ValueError):
        con = create_mq_connection("bad://127.0.0.1:8080/",_TOPIC)
