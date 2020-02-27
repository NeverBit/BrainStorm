import pika

class rabbitmq_conn:
    def __init__(self,host,port,topic):
        self.host = host
        self.port = port
        self.topic = topic
        # Create connection to MQ
        params = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=topic, exchange_type='fanout')

    def publish(self,msg):
        # publishing to the entire exchange
        self.channel.basic_publish(
            exchange = topic,
            routing_key = '',
            body = msg
        )
        
    def start_consume(self,callback):
        # Creating new nameless queue in the exchaange and consuming from it
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=topic, queue=queue_name)
        self.channel.basic_consume(
            queue = queue_name,
            auto_ack = True,
            on_message_callback = callback,
        )
        self.channel.start_consuming()