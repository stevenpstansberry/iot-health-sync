package org.example.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2ClientBuilder;
import com.amazonaws.services.ec2.model.RunInstancesRequest;
import com.amazonaws.services.ec2.model.IamInstanceProfileSpecification;

import java.util.Base64;

@RestController
public class JobController {

    @Value("${INSTANCE_AMI}")
    private String instanceAmi;

    @Value("${INSTANCE_TYPE}")
    private String instanceType;

    @Value("${INSTANCE_KEY_PAIR}")
    private String keyPairName;

    @Value("${INSTANCE_SECURITY_GROUP}")
    private String securityGroupName;

    @PostMapping("/start-job")
    public ResponseEntity<String> startJob() {
        try {
            String userDataScript = generateUserDataScript();
            launchEC2Instance(userDataScript);
            return ResponseEntity.ok("EC2 instance started for batch job!");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Failed to start EC2 instance: " + e.getMessage());
        }
    }

    private void launchEC2Instance(String userDataScript) {
        AmazonEC2 ec2 = AmazonEC2ClientBuilder.defaultClient();

        RunInstancesRequest runInstancesRequest = new RunInstancesRequest()
                .withImageId(instanceAmi)
                .withInstanceType(instanceType)
                .withKeyName(keyPairName)
                .withSecurityGroups(securityGroupName)
                .withMinCount(1)
                .withMaxCount(1)
                .withUserData(userDataScript)
                .withIamInstanceProfile(new IamInstanceProfileSpecification().withName("EC2Role"));

        ec2.runInstances(runInstancesRequest);
    }

    private String generateUserDataScript() {
        // Create a bash script to set up and run the simulation
        String script = "#!/bin/bash\n" +
                "sudo apt update && sudo apt install -y python3-pip nc\n" +
                "cd /home/ubuntu/scripts\n" +
                "bash simulate-iot-data.sh &\n" +
                "cd /home/ubuntu/backend\n" +
                "python3 server.py &\n" +
                "python3 consumer.py &\n" +
                "sleep 1800\n" +  // Wait for 30 minutes
                "sudo shutdown -h now\n"; // Shutdown the EC2 instance

        // Encode the script to Base64 (required for EC2 User Data)
        return Base64.getEncoder().encodeToString(script.getBytes());
    }
}
