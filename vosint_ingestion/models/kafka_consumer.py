# -*- coding: utf-8 -*-
from kafka import KafkaConsumer
from models.kafka_producer import KafkaProducer_class

import json

from automation.drivers import DriverFactory
from automation.storages import StorageFactory

from automation.pipeline import Pipeline_Kafka
class KafkaConsumer_class:
    def __init__(self):
        self.preducer = KafkaProducer_class()
        #self.driver = DriverFactory('playwright')
        self.storage = StorageFactory('hbase')

    def poll(self,topic,group_ids = 'group_id'):
        result = ''
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['192.168.1.63:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Tắt tự động commit offset
            group_id= group_ids,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )


        messages = consumer.poll(10000,1)
        for tp, messages in messages.items():
            for message in messages:
                # Xử lý message
                message = message.value
                
                try:
                    try:
                        result = self.excute(message)
                        
                        
                    except:
                        pass
                        #self.preducer.write(topic='crawling',message=message)
                    finally:
                        consumer.commit({
                            tp: {
                                'offset': message.offset + 1
                            }
                        })
                        consumer.commit_async()
                except:
                    # Nếu xử lý lỗi, không commit offset
                    pass
        consumer.commit_async()
        consumer.close()
        return result
    
    def excute(self,message):
        #a = message['id_proxy']
        #self.driver = DriverFactory(name='playwright',id_proxy=a)
        try:
            a = message['id_proxy']
            self.driver = DriverFactory(name='playwright',id_proxy=a)
        except:
            self.driver = DriverFactory('playwright')
        pipe_line = Pipeline_Kafka(driver=self.driver,storage=self.storage,actions=message['actions'],pipeline_id=message['kwargs']['pipeline_id'],mode_test=message['kwargs']['mode_test'],input_val = message['input_val'],kwargs=message['kwargs'])
        return pipe_line.run()








    