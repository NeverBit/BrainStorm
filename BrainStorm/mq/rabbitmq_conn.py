import pika

class rabbitmq_conn:
    def __init__(self,host,port,topic):
        self.host = host
        self.port = port
        self.topic = topic

    def open(self):
        # Create connection to MQ
        params = pika.ConnectionParameters(self.host, self.port)
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=self.topic, exchange_type='fanout')

    def publish(self,msg):
        # publishing to the entire exchange
        self.channel.basic_publish(
            exchange = self.topic,
            routing_key = '',
            body = msg
        )
        
    def start_consume(self,callback):
        # Creating new nameless queue in the exchange and consuming from it
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.topic, queue=queue_name)
        self.channel.basic_consume(
            queue = queue_name,
            auto_ack = True,
            on_message_callback = callback,
        )
        self.channel.start_consuming()