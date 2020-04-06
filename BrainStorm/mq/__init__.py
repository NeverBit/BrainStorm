from furl import furl
from .rabbitmq_conn import rabbitmq_conn


mq_schemes_to_classes = {'rabbitmq': rabbitmq_conn}


def create_mq_connection(connection_string, exchange):
    url = furl(connection_string)
    print(f' @@@ DEBUG Scheme: {url.scheme}')
    if (url.scheme not in mq_schemes_to_classes):
        raise ValueError(
            f'Unsupported scheme "{url.scheme}" for MQ connection string')

    mq_class = mq_schemes_to_classes[url.scheme]

    host = url.host
    port = url.port
    if(port is None):
        raise ValueError(
            f'Port must be explicitly given in MQ connection string')
    print(f' @@@ Debug Found {url.scheme} mq connection info: {host}:{port}')
    conn = mq_class(host, port, exchange)
    print(f' @@@ Debug connection object {conn}')
    return conn
