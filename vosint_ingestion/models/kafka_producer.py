# -*- coding: utf-8 -*-
import json
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from models.kafka_python import Kafka_class
class KafkaProducer_class:
    def __init__(self):
        # Create a Kafka producer object
        self.producer = KafkaProducer(
            bootstrap_servers=['192.168.1.63:9092']
        )
           
    def write(self, topic: str, message):
        # if not self.check_topic_exist(topic):
        #     Kafka_class().create_topic(topic,5,1)
        json_message = json.dumps(message).encode('utf-8')
        self.producer.send(topic, json_message)
        self.producer.flush()
        self.producer.close()

    def check_topic_exist(self,topic_name):
        #print(1)
        admin_client = KafkaAdminClient(bootstrap_servers=['192.168.1.63:9092'])
        #print(2)
        topic_metadata = admin_client.list_topics()
        #print(3)
        if topic_name not in set(t for t in topic_metadata):
            return False
        else:
            return True
# #Xóa topic
# from kafka.admin import KafkaAdminClient, NewTopic

# # Tạo một KafkaAdminClient object với bootstrap servers
# admin_client = KafkaAdminClient(bootstrap_servers=['192.168.1.63:9092'])

# # Xác định topic cần xóa
# topic_to_delete = "crawling_"

# # Sử dụng method delete_topics() trên admin_client để xóa topic
# admin_client.delete_topics([topic_to_delete])

# # Kiểm tra xem topic đã được xóa thành công hay chưa
# topic_metadata = admin_client.list_topics()
# print('list_topic',topic_metadata)
# if topic_to_delete not in set(t for t in topic_metadata):
#     print(f"Topic {topic_to_delete} has been deleted")
# else:
#     print(f"Failed to delete topic {topic_to_delete}")
            
        