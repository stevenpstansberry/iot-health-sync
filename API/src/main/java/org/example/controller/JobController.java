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
        // Bash script to start Zookeeper, Kafka, Redis, and application scripts
        String script = "#!/bin/bash\n" +
                "# Start Zookeeper\n" +
                "nohup /opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties > /var/log/zookeeper.log 2>&1 &\n" +
                "sleep 5\n" +  // Wait for Zookeeper to start\n" +
                "# Start Kafka\n" +
                "nohup /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties > /var/log/kafka.log 2>&1 &\n" +
                "sleep 5\n" +  // Wait for Kafka to start\n" +
                "# Start Redis\n" +
                "sudo systemctl start redis-server\n" +
                "sleep 2\n" +  // Wait for Redis to start\n" +
                "# Run the IoT simulation script\n" +
                "cd /home/ubuntu/scripts\n" +
                "bash simulate-iot-data.sh &\n" +
                "# Run backend Python scripts\n" +
                "cd /home/ubuntu/backend\n" +
                "python3 server.py &\n" +
                "python3 consumer.py &\n" +
                "# Wait 30 minutes\n" +
                "sleep 1800\n" +
                "# Shut down EC2 instance\n" +
                "sudo shutdown -h now\n";

        // Encode the script to Base64 (required for EC2 User Data)
        return Base64.getEncoder().encodeToString(script.getBytes());
    }
}
