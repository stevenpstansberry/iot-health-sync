# IoT Health Sync

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

- Utilizes Bash scripts and netcat for IoT device simulation, sending telemetry via TCP sockets.
- Monitors Kafka, Redis, and network traffic with Unix tools such as `tcpdump`, `htop`, and `netstat`.

### Secure Networking

- Implements firewall rules (`iptables`) and SSL/TLS encryption to secure data transmission.
- Enforces data encryption at rest and in transit using the AES-256 encryption algorithm.

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
- **Amazon S3**: Archives historical data for compliance and analytics with AES-256 encryption for data at rest.

### APIs

- Backend services expose:
  - REST APIs for real-time and historical data retrieval.

### System Monitoring

- Unix tools (`tcpdump`, `netstat`) debug and optimize networking and data flow.

### Security

- SSL/TLS encryption ensures secure data transfer with AES-256 encryption applied to transmitted data.
- Firewalls (`iptables`) restrict access to Kafka and Redis.
- Data at rest in both Redis and Amazon S3 is encrypted using AES-256, ensuring compliance with industry security standards.

---

## Workflow

### IoT Simulation

- Unix scripts simulate telemetry data (e.g., `heart_rate=78, oxygen=95%`) alongside patient information and transmit it via TCP sockets.

### Data Ingestion

- Backend socket server validates data and forwards it to Kafka topics.
- Kafka Streams detects anomalies and formats data into FHIR/HIPAA-compliant JSON.

### Data Storage

- Redis caches real-time data and anomalies before forwarding to Amazon S3 for long-term archiving.

### Data Encryption

- **Data in Transit**: Secured with SSL/TLS, ensuring that all communication between IoT devices, the backend, and storage is encrypted using the AES-256 algorithm.
- **Data at Rest**: Redis and Amazon S3 use AES-256 encryption to protect sensitive information stored within the system.

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

- Redis for low-latency access to anomalies and Amazon S3 for long-term archiving.

- The S3 Lambda Access Point ensures that data stripped of PII is archived in compliance with privacy regulations.

### Backend

- Spring Boot for REST APIs and cron job orchestration.

### Security and Encryption

- AES-256 encryption for data at rest and in transit.
- SSL/TLS protocols for secure communication.

### System Monitoring

- Unix tools (`tcpdump`, `netstat`, `htop`).

---
