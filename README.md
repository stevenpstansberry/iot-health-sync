# Iot Health Sync

## Objective

This project focuses on designing and deploying a scalable, secure IoT system for real-time monitoring of patient vitals such as heart rate, oxygen saturation, and temperature. The system incorporates Kafka for data ingestion, Redis for low-latency storage, and adheres to FHIR standards for healthcare interoperability. Enhanced with Unix networking tools, it demonstrates proficiency in IoT systems, networking, and system-level monitoring.

---

## Key Features

### Real-Time Data Pipeline

- Collects, processes, and analyzes telemetry data from simulated IoT devices in real-time using Kafka Streams.
- Detects anomalies in patient vitals (e.g., oxygen levels dropping below safe thresholds).

### Interoperability

- Formats telemetry data into FHIR-compliant JSON for integration with healthcare systems like EHRs (Electronic Health Records).

### Unix-Based Simulation and Monitoring

- Utilizes Bash scripts and netcat for IoT device simulation, sending telemetry via TCP/UDP sockets.
- Monitors Kafka, Redis, and network traffic with Unix tools such as `tcpdump`, `htop`, and `netstat`.

### Secure Networking

- Implements firewall rules (`iptables`) and SSL/TLS encryption to secure data transmission.

### Fast Data Access and Archiving

- Leverages Redis for caching recent vitals and Amazon S3 for archiving historical data.

### System Health Monitoring

- Cloudwatch monitors output statements.

---

## Architecture Overview

### IoT Devices

- Simulated devices (via Unix scripts) send patient vitals (e.g., heart rate, oxygen saturation) over TCP sockets.

### Networking Layer

- A Python socket server validates telemetry and forwards data to Kafka topics for processing.

### Data Pipeline

- Kafka Streams processes incoming data for:
  - Anomaly detection.
  - Formatting telemetry into FHIR/HIPAA-compliant JSON.
- Anomalies are flagged and forwarded to Redis.

### Data Storage

- **Redis**: Caches live patient vitals for quick dashboard access.
- **Amazon S3**: Archives historical data for compliance and analytics.

### APIs

- Backend services expose:
  - REST APIs for real-time and historical data retrieval.

### System Monitoring

- Unix tools (`tcpdump`, `netstat`) debug and optimize networking and data flow.

### Security

- SSL encryption ensures secure data transfer.
- Firewalls (`iptables`) restrict access to Kafka and Redis.

---

## Workflow

### IoT Simulation

- Unix scripts simulate telemetry data (e.g., `heart_rate=78, oxygen=95%`) and transmit it via TCP sockets.

### Data Ingestion

- Backend socket server validates data and forwards it to Kafka topics.
- Kafka Streams detects anomalies and formats data into FHIR/HIPAA-compliant JSON.

### Data Storage

- Redis caches real-time data and anomalies before forwarding to Amazon S3 for long-term archiving.

### System Monitoring

- Unix tools (`tcpdump`, `htop`) debug and optimize data flow.

---

## Technologies Used

### IoT Simulation

- Bash scripts, `netcat`, and cron jobs for periodic data generation.

### Data Pipeline

- Apache Kafka and Kafka Streams for ingestion and processing.

### Networking

- TCP sockets, `iptables` for firewalls, and HAProxy for load balancing.

### Storage

- Redis for low-latency access of anamolies and Amazon S3 for long term archiving.

- The S3 Lambda Access Point ensures that data stripped of PII is archived in compliance with privacy regulations.

### Backend

- Spring Boot for REST APIs and cron job orchestration

### System Monitoring

- Unix tools (`tcpdump`, `netstat`, `htop`).

---

## Deliverables

1. **Fully Functional IoT Pipeline**

   - Real-time telemetry processing with anomaly detection.
   - FHIR-compliant JSON data formatting.

2. **Interactive Dashboard**

   - Real-time visualization of patient data, alerts, and trends.

3. **Networking and Security**
   - Socket-based communication, TLS encryption, and firewall rules.

---

## Why This Project Stands Out

### Multi-Disciplinary Skill Set

- Combines IoT, networking, real-time processing, Unix, and web development.

### Real-World Relevance

- Adheres to healthcare standards (FHIR, HIPAA), ensuring deployability in real-world environments.

### Competitive Edge

- Unix and networking skills add a unique dimension to traditional IoT projects.

---
