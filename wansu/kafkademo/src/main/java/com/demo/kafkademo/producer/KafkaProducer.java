package com.demo.kafkademo.producer;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class KafkaProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;

    public void sendMessage(String message) {
        kafkaTemplate.send("test-topic", message);
        System.out.println("Sent Message: " + message);
    }
}
