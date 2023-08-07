import argparse, json, os
from pub_sub_api import KafkaClient


class TransactionClassifier:

    # Método construtor da classe TransactionClassifier
    def __init__(self, network):
        self.network = network


    # Método para classificar as transações e enviar para o Kafka ou EventHub
    def __classify_transaction(self, transaction) -> None:
        if transaction['input'] == '0x': 
            topic = f'{self.network}_simple_transaction'
        elif transaction['to'] == None:
            topic = f'{self.network}_contract_deployment'
        else: 
            topic = f'{self.network}_contract_interaction'
        return topic, transaction 


    def classify_transactions(self, topic_consumer):
        for msg in topic_consumer:
            tx = json.loads(msg.value)
            topic, transaction = self.__classify_transaction(tx)
            yield topic, transaction



if __name__ == '__main__':

    network = os.environ["NETWORK"]
    kafka_host = os.environ["KAFKA_ENDPOINT"]
    topic_consume = f'{network}_{os.environ["TOPIC_CONSUME"]}'
    group_id = os.environ.get('CONSUMER_GROUP', 'group_1')

    tx_classifier = TransactionClassifier(network)
    kafka_client = KafkaClient(connection_str=kafka_host)
    producer = kafka_client.create_producer()
    consumer = kafka_client.create_consumer(topic=topic_consume, consumer_group=group_id)
    for topic, transaction in tx_classifier.classify_transactions(consumer):
        kafka_client.send_data(producer, topic, transaction)
        print(f"Transaction sent to {topic}")

  
