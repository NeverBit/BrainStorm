import threading
import time
import pika


class rabbitmq_conn:
    def __init__(self, host, port, exchange):
        self.host = host
        self.port = port
        self.exchange = exchange

    def open(self):
        # Create connection to MQ (try multiple times)
        for i in range(100):
            try:
                params = pika.ConnectionParameters(self.host, self.port)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                self.channel.basic_qos(prefetch_count=1)
                self.channel.exchange_declare(exchange=self.exchange,
                                              exchange_type='topic')
                break
            except Exception:
                time.sleep(1)
                continue

    def close(self):
        self.connection.close()

    def publish(self, msg, topic='default_topic'):
        # publishing to the entire exchange
        self.channel.basic_publish(exchange=self.exchange, routing_key=topic,
                                   body=msg)

    def start_consume(self, callback, topics=None):
        # Creating new nameless queue in the exchange and consuming from it
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        # If caller provided topic(s) to bind to - user them.
        # Otherwise use '#' which consumes all topics
        if not topics:
            topics = ('#')
        for binding_key in topics:
            self.channel.queue_bind(exchange=self.exchange,
                                    queue=queue_name,
                                    routing_key=binding_key)

        # Wrap the callback with auto-heartbeat callback
        def cb(ch, method, properties, body):
            if callback is not None:
                # Running actual callback on another thread
                # and using the current thread to gurentee
                # that heartbeats to the MQ will continue
                # (Crucial if the callback might take a long time)
                t = threading.Thread(target=callback, args=(ch,
                                                            method,
                                                            properties,
                                                            body))
                t.daemon = True
                t.start()

                while t.is_alive():
                    self.connection.process_data_events()
                    self.connection.sleep(1)

        self.channel.basic_consume(queue=queue_name, auto_ack=True,
                                   on_message_callback=cb)
        self.channel.start_consuming()
