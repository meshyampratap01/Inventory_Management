#  Inventory Management System

A production-ready backend inventory management system for small shops to **track stock levels, manage incoming/outgoing inventory, and receive automated low-stock alerts**.

Built with FastAPI and deployed on AWS using containers, managed databases, and event-driven services.

---

#  Problem Statement

Design a backend inventory system for a small shop to:

- Track stock levels  
- Record incoming and outgoing inventory  
- Detect low-stock situations  
- Send alerts when inventory falls below thresholds  

This system is designed to be **scalable, fault-tolerant, and production-ready**, suitable for real-world small business usage.

---

#  Overview

This system follows a **containerized + event-driven architecture**:

- Synchronous operations handled by a REST API  
- Asynchronous low-stock alerts via messaging services  
- Managed authentication & role-based access  
- Fully deployed on AWS infrastructure  

---

#  Architecture Diagram

<img width="761" height="626" alt="ivvm drawio" src="https://github.com/user-attachments/assets/5d1f6d0f-c715-492e-9af8-0f2b69235ac3" />



---

## Core API (Containerized)

- FastAPI application running on AWS ECS  
- Exposed via Application Load Balancer (ALB)  

Handles:

- Inventory creation  
- Stock updates  
- Incoming/outgoing transactions  
- Inventory queries  

### Why ECS?

- Predictable performance  
- No cold starts  
- Better for consistent traffic  
- Easy horizontal scaling  

---

## Database

- Amazon DynamoDB  
- PAY_PER_REQUEST billing  
- Low latency reads/writes  
- Scales automatically  

---

## Low-Stock Alert Pipeline (Event-Driven)

When stock falls below a threshold:

1. Application publishes event to SNS  
2. SNS fan-outs to SQS  
3. SQS triggers Lambda  
4. Lambda processes low-stock notifications  

### Why this design?

- Decouples alerting from API  
- Prevents blocking requests  
- Reliable retries  
- Easily extensible  

---

# Email Alert Screenshots

<img width="710" height="727" alt="image" src="https://github.com/user-attachments/assets/784774df-f1e7-495a-a07c-7d12a6921ac5" />


---

#  Authentication & Authorization

Authentication is managed using **Amazon Cognito**.

## Role-Based Access Control (RBAC)

Two roles are supported:

###  Manager

- Create inventory items  
- Update stock levels  
- Configure low-stock thresholds  
- View all inventory records  
- Access analytics-ready endpoints  

###  Staff

- View inventory  
- Update incoming/outgoing stock  
- Limited modification rights  

All protected endpoints require valid Cognito JWT tokens.

---

#  Data Flow

1. Client sends authenticated request → API  
2. API validates Cognito JWT  
3. API updates DynamoDB  
4. If stock < threshold → event sent to SNS  
5. SNS → SQS → Lambda  
6. Lambda processes alert  

---

#  Key Features

## Inventory Management

- Create inventory items  
- Update stock levels  
- Track incoming stock  
- Track outgoing stock  
- Configurable thresholds  

---

## Low-Stock Alerts

- Automatic detection  
- Asynchronous processing  
- Reliable delivery via queues  

---

## Scalability

- ECS horizontal scaling  
- DynamoDB auto-scaling  
- Event-driven architecture  

---

## Reliability

- Message durability with SQS  
- Retry mechanisms  
- Stateless API design  

---

#  Testing

- Unit testing with Python `unittest`  
- **94% test coverage**

Covers:

- Business logic  
- API validation  
- Inventory workflows  

Run tests:

```bash
python -m unittest discover 
```

---

#  Project Structure

```
inventory_management_eval/
│
├── app/
│   ├── app_exception/        # Custom exception handling
│   ├── dto/                  # Request/response DTOs (Pydantic models)
│   ├── models/               # DynamoDB data models
│   ├── repository/           # Data access layer
│   ├── response/             # Standardized API responses
│   ├── routes/               # FastAPI route definitions
│   ├── services/             # Business logic layer
│   ├── sns_event_publisher/  # SNS event publishing logic
│   ├── utils/                # Helper utilities
│   ├── dependencies.py       # Dependency injection
│   ├── app.py                # FastAPI entry point
│   └── __init__.py
│
├── lambdas/                  # Lambda functions for low-stock alerts
│
├── deploy/                   # Deployment configurations (SAM/infra)
│
├── tests/                    # Unit tests
│
├── Dockerfile                # Container definition
├── requirements.txt          # Python dependencies
└── samconfig.toml            # AWS SAM configuration
```

---

- **Routes → Services → Repository → DynamoDB**
- Clear separation of concerns
- Highly testable and maintainable
- Easy to scale and extend

# AWS Deployment

## Prerequisites

- AWS CLI configured  
- ECR repository  
- VPC with public/private subnets  
- Cognito User Pool configured  

---

## Build & Push Image

```bash
docker build -t inventory-app .

docker tag inventory-app:latest <account-id>.dkr.ecr.<region>.amazonaws.com/inventory-app:latest

docker push <ecr-uri>
```

---

## Deploy on ECS

- Create ECS service  
- Attach ALB  
- Configure health checks  
- Set environment variables  

---

#  Security Considerations

- Cognito-based authentication  
- Role-based access control  
- IAM least privilege  
- No hardcoded credentials  
- Private subnets for containers  

---

#  Future Improvements

- CloudWatch alarms  
- Admin dashboard  
- Inventory analytics  
- Multi-store support  

---

#  Author

**Shyam Pratap**

Backend & Cloud Developer passionate about building scalable systems on AWS.
