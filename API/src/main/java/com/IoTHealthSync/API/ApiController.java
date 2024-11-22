package com.IoTHealthSync.API;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class ApiController {

    @RequestMapping("/api/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }

}
