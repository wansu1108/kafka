package com.demo.kafkademo.producer;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/demo")
@RequiredArgsConstructor
public class DemoController {
    
    private final KafkaProducer kafkaProducer;
    
    @GetMapping("/send")
    public String send(@RequestParam String message) {
        kafkaProducer.sendMessage(message);
        return "Message Sent: " + message;
    }
}
