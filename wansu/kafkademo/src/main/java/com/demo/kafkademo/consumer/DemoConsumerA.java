package com.demo.kafkademo.consumer;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class DemoConsumerA {

    @KafkaListener(topics = "test-topic", groupId = "test-groupA")
    public void consume(String message) {
        System.out.println("[A] Received message: " + message);
    }
}
