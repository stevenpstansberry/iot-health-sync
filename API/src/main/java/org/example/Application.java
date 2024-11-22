package org.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

import org.example.controller.PingController;
import org.example.controller.HealthController;

@SpringBootApplication
// Explicitly import controllers for faster cold starts
@Import({ PingController.class, HealthController.class })
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
