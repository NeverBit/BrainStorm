import re
from .rabbitmq_conn import rabbitmq_conn

# TODO: furl
rmq_parser_regex = re.compile(r'rabbitmq://(\d+\.\d+\.\d+\.\d+):(\d+)/')

def create_mq_connection(connection_string,topic):
    print(' @@@ DEBUG parsing '+connection_string)
    print(f' @@@ DEBUG with {rmq_parser_regex}')
    rmq_match = rmq_parser_regex.search(connection_string)
    print('res:')
    print(rmq_match)
    if(rmq_match == None):
        raise ValueError('Unsupported format for connection string')
    host = rmq_match.group(1)
    port = rmq_match.group(2)
    print(f'Found rabbit mq connection info: {host}:{port}')
    conn = rabbitmq_conn(host,port,topic)
    print(f' @@@ Debug connection object {conn}')
    return conn
