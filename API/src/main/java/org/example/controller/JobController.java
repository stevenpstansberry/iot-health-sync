package org.example.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2ClientBuilder;
import com.amazonaws.services.ec2.model.StartInstancesRequest;

@RestController
public class JobController {

    // Inject the EC2 Instance ID from the environment
    @Value("${INSTANCE_ID}")
    private String instanceId;

    @PostMapping("/start-job")
    public ResponseEntity<String> startJob() {
        try {
            triggerEC2Instance();
            return ResponseEntity.ok("EC2 instance started for batch job!");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Failed to start EC2 instance: " + e.getMessage());
        }
    }

    private void triggerEC2Instance() {
        AmazonEC2 ec2 = AmazonEC2ClientBuilder.defaultClient();
        StartInstancesRequest request = new StartInstancesRequest()
                .withInstanceIds(instanceId);
        ec2.startInstances(request);
    }
}
