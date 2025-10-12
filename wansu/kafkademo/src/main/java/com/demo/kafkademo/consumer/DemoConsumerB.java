package com.demo.kafkademo.consumer;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class DemoConsumerB {

    @KafkaListener(topics = "test-topic", groupId = "test-groupB")
    public void consume(String message) {
        System.out.println("[B] Received message: " + message);
    }
}
