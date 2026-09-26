                                                    Smart Hospital Management System (HMIS)
                                                    The Smart Hospital Management System (HMIS) is a multi-tenant, cloud-native enterprise platform designed to manage hospital operations, patient records, billing, tenant administration, and medical imaging workflows.

The repository contains an asynchronous Python backend (FastAPI/SQLAlchemy), PostgreSQL/Aurora database migrations (Alembic), DICOM medical imaging web components (React), Infrastructure as Code (Terraform for AWS ECS/Aurora/KMS/S3/OIDC), and continuous integration pipelines (GitHub Actions).

---

## 📂 Repository Structure

```text
Smart-Hospital-Management-System/
├── .github/
│   └── workflows/
│       └── terraform.yml          # CI/CD pipeline for Terraform lint & plan
├── alembic/                       # Alembic database migration scripts and env setup
├── app/
│   ├── repositories/              # Async Data access layer (AppointmentRepository, etc.)
│   ├── api/                       # Multi-tenant hospital & administrative API endpoints
│   └── config.py                  # Core application configuration settings
├── react/
│   └── WebDicomViewerContainer/   # React component for browser DICOM rendering
├── terraform/                     # Infrastructure as Code (AWS Provisioning)
│   ├── aurora.tf                  # Amazon Aurora PostgreSQL cluster config
│   ├── backend-bootstrap.tf       # S3 & DynamoDB remote state bootstrapping
│   ├── ecs.tf                     # ECS Fargate cluster, task definitions, & services
│   ├── kms.tf                     # Customer Managed Keys (CMK) for data encryption
│   ├── oidc-github.tf             # AWS IAM OpenID Connect provider for GitHub Actions
│   ├── s3.tf                      # Encrypted S3 buckets for hospital assets
│   └── vpc.tf                     # Multi-AZ VPC network isolation
├── Dockerfile                     # Multi-stage Python production build file
└── docker-compose.yml             # Local multi-container development environment

git clone https://github.com/Bashyalsantosh/Smart-Hospital-Management-System.git
cd Smart-Hospital-Management-System

DATABASE_URL=postgresql+asyncpg://hmis_user:hmis_password@localhost:5432/hmis_db
SECRET_KEY=super-secret-production-key
ENVIRONMENT=development

docker-compose exec backend alembic upgrade head

git clone [https://github.com/Bashyalsantosh/Smart-Hospital-Management-System.git](https://github.com/Bashyalsantosh/Smart-Hospital-Management-System.git)
cd Smart-Hospital-Management-System


DATABASE_URL=postgresql+asyncpg://hmis_user:hmis_password@localhost:5432/hmis_db
SECRET_KEY=super-secret-production-key
ENVIRONMENT=development

docker-compose up -d --build


docker-compose exec backend alembic upgrade head









├── docker-compose.aws.yml         # AWS-specific local emulation container layout
└── template.yaml                  # AWS SAM serverless infrastructure specification
