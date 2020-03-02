import pika

class rabbitmq_conn:
    def __init__(self,host,port,exchange):
        self.host = host
        self.port = port
        self.exchange = exchange

    def open(self):
        # Create connection to MQ
        params = pika.ConnectionParameters(self.host, self.port)
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic')

    def publish(self,msg,topic='default_topic'):
        # publishing to the entire exchange
        self.channel.basic_publish(
            exchange = self.exchange,
            routing_key = topic,
            body = msg
        )
        
    def start_consume(self,callback,topics=None):
        # Creating new nameless queue in the exchange and consuming from it
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        # If caller provided topic(s) to bind to - user them.
        # Otherwise use '#' which consumes all topics
        if not topics:
            topics = ('#')
        for binding_key in topics:
            self.channel.queue_bind(exchange=self.topic,
                                    queue=queue_name, 
                                    routing_key=binding_key)

        self.channel.basic_consume(
            queue = queue_name,
            auto_ack = True,
            on_message_callback = callback,
        )
        self.channel.start_consuming()