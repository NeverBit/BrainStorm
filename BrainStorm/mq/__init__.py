from furl import furl
import re
from .rabbitmq_conn import rabbitmq_conn

# TODO: furl
rmq_parser_regex = re.compile(r'rabbitmq://(\d+\.\d+\.\d+\.\d+):(\d+)/')


def create_mq_connection(connection_string, topic):
    url = furl(connection_string)
    print(f' @@@ DEBUG Scheme: {url.scheme}')
    if (url.scheme != 'rabbitmq'):
        raise ValueError(
            f'Unsupported scheme "{url.scheme}" for MQ connection string')
    host = url.host
    port = url.port
    if(port is None):
        raise ValueError(
            f'Port must be explicitly given in MQ connection string')
    print(f'Found rabbit mq connection info: {host}:{port}')
    conn = rabbitmq_conn(host, port, topic)
    print(f' @@@ Debug connection object {conn}')
    return conn
