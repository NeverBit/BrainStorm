from furl import furl
from .rabbitmq_conn import rabbitmq_conn


mq_schemes_to_classes = {'rabbitmq': rabbitmq_conn}


def create_mq_connection(connection_string, exchange):
    url = furl(connection_string)
    if (url.scheme not in mq_schemes_to_classes):
        raise ValueError(
            f'Unsupported scheme "{url.scheme}" for MQ connection string')

    mq_class = mq_schemes_to_classes[url.scheme]

    host = url.host
    port = url.port
    if(port is None):
        raise ValueError(
            f'Port must be explicitly given in MQ connection string')
    conn = mq_class(host, port, exchange)
    return conn
