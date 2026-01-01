"""
Deployment Blueprint Generation Contract

Backend API for generating infrastructure-as-code templates for cloud deployments.
Implemented as agent skills using Jinja2 templates.
"""

from typing import Dict, List, Literal, Any
from pydantic import BaseModel, Field
from enum import Enum


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class Environment(str, Enum):
    """Deployment environments."""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class OutputFormat(str, Enum):
    """Infrastructure-as-code output formats."""
    TERRAFORM = "terraform"  # .tf files (HCL)
    CLOUDFORMATION = "cloudformation"  # .yaml (AWS native)
    ARM_TEMPLATE = "arm"  # .json (Azure native)


class SecretReference(BaseModel):
    """Reference to cloud secrets manager secret."""
    name: str  # Logical name (e.g., "db_password")
    provider: Literal["aws-secrets-manager", "gcp-secret-manager", "azure-keyvault"]
    path: str  # Secret ARN/ID (e.g., "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/db/password")
    description: str  # Human-readable description


class ScalingConfig(BaseModel):
    """Auto-scaling configuration."""
    min_instances: int = Field(ge=1, le=100)
    max_instances: int = Field(ge=1, le=1000)
    target_cpu_utilization: int = Field(ge=1, le=100, default=70)  # Percentage


class BlueprintParameters(BaseModel):
    """User-provided blueprint configuration."""
    provider: CloudProvider
    environment: Environment
    region: str  # e.g., "us-east-1", "us-central1", "eastus"
    app_name: str  # Application name (used in resource naming)

    # Compute configuration
    instance_type: str  # e.g., "t3.micro", "e2-micro", "B1S"
    runtime: str  # e.g., "python3.11", "nodejs18"
    scaling: ScalingConfig

    # Database configuration
    database_type: str  # e.g., "postgres", "mysql", "dynamodb"
    database_instance_class: str  # e.g., "db.t3.micro"

    # Networking
    enable_vpc: bool = True
    allowed_cidr_blocks: List[str] = ["0.0.0.0/0"]  # Default: public (dev only)

    # Secrets
    secrets: List[SecretReference] = []


class GeneratedFile(BaseModel):
    """Generated infrastructure-as-code file."""
    filename: str  # e.g., "main.tf", "variables.tf", "outputs.tf"
    content: str  # File content
    language: str  # e.g., "hcl", "yaml", "json"


class BlueprintGenerationResult(BaseModel):
    """Result of blueprint generation."""
    blueprint_id: str  # UUID
    provider: CloudProvider
    environment: Environment
    output_format: OutputFormat
    generated_at: str  # ISO 8601 timestamp
    files: List[GeneratedFile]
    secrets_setup_instructions: str  # Markdown instructions for pre-creating secrets
    deployment_instructions: str  # Markdown instructions for deploying


class BlueprintValidationResult(BaseModel):
    """Result of blueprint validation."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    estimated_cost_monthly_usd: float | None = None  # Rough estimate


# ============================================================================
# API Endpoint Contracts
# ============================================================================

class GenerateBlueprintRequest(BaseModel):
    """Request to generate deployment blueprint."""
    parameters: BlueprintParameters
    output_format: OutputFormat


class GenerateBlueprintResponse(BaseModel):
    """Response from blueprint generation."""
    result: BlueprintGenerationResult


# ============================================================================
# Skill Contracts
# ============================================================================

from contracts.agent_skills import skill


@skill(name="generate_aws_blueprint", version="1.0.0")
def generate_aws_blueprint(params: BlueprintParameters) -> BlueprintGenerationResult:
    """
    Generate AWS infrastructure blueprint (Terraform or CloudFormation).

    Generates:
        - Lambda function + API Gateway (compute)
        - RDS or DynamoDB (database)
        - VPC + subnets + security groups (networking)
        - IAM roles and policies (permissions)
        - Secrets Manager integration (secrets)
        - CloudWatch logs (monitoring)

    Args:
        params: Blueprint configuration

    Returns:
        Generated blueprint with Terraform/CloudFormation files

    Example:
        >>> params = BlueprintParameters(
        ...     provider=CloudProvider.AWS,
        ...     environment=Environment.PRODUCTION,
        ...     region="us-east-1",
        ...     app_name="todo-chatbot",
        ...     instance_type="t3.micro",
        ...     runtime="python3.11",
        ...     scaling=ScalingConfig(min_instances=2, max_instances=10),
        ...     database_type="postgres",
        ...     database_instance_class="db.t3.micro",
        ...     secrets=[
        ...         SecretReference(
        ...             name="db_password",
        ...             provider="aws-secrets-manager",
        ...             path="arn:aws:secretsmanager:us-east-1:123:secret:prod/db/password",
        ...             description="PostgreSQL database password"
        ...         )
        ...     ]
        ... )
        >>> result = generate_aws_blueprint(params)
        >>> print(result.files[0].filename)  # "main.tf"
    """
    ...


@skill(name="generate_gcp_blueprint", version="1.0.0")
def generate_gcp_blueprint(params: BlueprintParameters) -> BlueprintGenerationResult:
    """
    Generate GCP infrastructure blueprint (Terraform).

    Generates:
        - Cloud Functions or Cloud Run (compute)
        - Cloud SQL (database)
        - VPC + firewall rules (networking)
        - IAM roles and service accounts (permissions)
        - Secret Manager integration (secrets)
        - Cloud Logging (monitoring)

    Args:
        params: Blueprint configuration

    Returns:
        Generated blueprint with Terraform files

    Example:
        >>> params = BlueprintParameters(
        ...     provider=CloudProvider.GCP,
        ...     environment=Environment.STAGING,
        ...     region="us-central1",
        ...     app_name="todo-chatbot",
        ...     instance_type="e2-micro",
        ...     runtime="python311",
        ...     scaling=ScalingConfig(min_instances=1, max_instances=5),
        ...     database_type="postgres",
        ...     database_instance_class="db-f1-micro",
        ...     secrets=[
        ...         SecretReference(
        ...             name="db_password",
        ...             provider="gcp-secret-manager",
        ...             path="projects/123/secrets/db-password/versions/latest",
        ...             description="PostgreSQL database password"
        ...         )
        ...     ]
        ... )
        >>> result = generate_gcp_blueprint(params)
    """
    ...


@skill(name="generate_azure_blueprint", version="1.0.0")
def generate_azure_blueprint(params: BlueprintParameters) -> BlueprintGenerationResult:
    """
    Generate Azure infrastructure blueprint (ARM template or Terraform).

    Generates:
        - Azure Functions (compute)
        - Azure Database for PostgreSQL/MySQL (database)
        - VNet + NSG (networking)
        - Managed Identity + RBAC (permissions)
        - Key Vault integration (secrets)
        - Application Insights (monitoring)

    Args:
        params: Blueprint configuration

    Returns:
        Generated blueprint with ARM template or Terraform files

    Example:
        >>> params = BlueprintParameters(
        ...     provider=CloudProvider.AZURE,
        ...     environment=Environment.DEV,
        ...     region="eastus",
        ...     app_name="todo-chatbot",
        ...     instance_type="B1",
        ...     runtime="python|3.11",
        ...     scaling=ScalingConfig(min_instances=1, max_instances=3),
        ...     database_type="postgres",
        ...     database_instance_class="B_Gen5_1",
        ...     secrets=[
        ...         SecretReference(
        ...             name="db-password",
        ...             provider="azure-keyvault",
        ...             path="https://my-vault.vault.azure.net/secrets/db-password",
        ...             description="PostgreSQL database password"
        ...         )
        ...     ]
        ... )
        >>> result = generate_azure_blueprint(params)
    """
    ...


@skill(name="validate_blueprint", version="1.0.0")
def validate_blueprint(params: BlueprintParameters) -> BlueprintValidationResult:
    """
    Validate blueprint parameters before generation.

    Validates:
        - Provider-specific instance types are valid
        - Region is valid for selected provider
        - Scaling configuration is sensible (min < max)
        - Database type supported by provider
        - Secret references match provider
        - CIDR blocks are valid
        - Cost estimation (if possible)

    Args:
        params: Blueprint configuration to validate

    Returns:
        Validation result with errors and warnings

    Example:
        >>> params = BlueprintParameters(
        ...     provider=CloudProvider.AWS,
        ...     environment=Environment.PRODUCTION,
        ...     region="invalid-region",
        ...     app_name="todo-chatbot",
        ...     instance_type="t9.invalid",
        ...     runtime="python3.11",
        ...     scaling=ScalingConfig(min_instances=10, max_instances=5),  # Invalid
        ...     database_type="postgres",
        ...     database_instance_class="db.t3.micro"
        ... )
        >>> result = validate_blueprint(params)
        >>> result.is_valid
        False
        >>> result.errors
        [
            "Invalid region 'invalid-region' for provider AWS",
            "Invalid instance type 't9.invalid' for AWS",
            "Scaling min_instances (10) must be less than max_instances (5)"
        ]
    """
    ...


# ============================================================================
# REST API Endpoint (FastAPI)
# ============================================================================

"""
POST /api/blueprints/generate
Content-Type: application/json

Request:
{
  "parameters": {
    "provider": "aws",
    "environment": "production",
    "region": "us-east-1",
    "app_name": "todo-chatbot",
    "instance_type": "t3.micro",
    "runtime": "python3.11",
    "scaling": {
      "min_instances": 2,
      "max_instances": 10,
      "target_cpu_utilization": 70
    },
    "database_type": "postgres",
    "database_instance_class": "db.t3.micro",
    "enable_vpc": true,
    "allowed_cidr_blocks": ["10.0.0.0/16"],
    "secrets": [
      {
        "name": "db_password",
        "provider": "aws-secrets-manager",
        "path": "arn:aws:secretsmanager:us-east-1:123:secret:prod/db/password",
        "description": "PostgreSQL database password"
      }
    ]
  },
  "output_format": "terraform"
}

Response (200 OK):
{
  "result": {
    "blueprint_id": "550e8400-e29b-41d4-a716-446655440000",
    "provider": "aws",
    "environment": "production",
    "output_format": "terraform",
    "generated_at": "2025-12-31T12:00:00Z",
    "files": [
      {
        "filename": "main.tf",
        "content": "resource \"aws_lambda_function\" \"main\" { ... }",
        "language": "hcl"
      },
      {
        "filename": "variables.tf",
        "content": "variable \"region\" { ... }",
        "language": "hcl"
      },
      {
        "filename": "outputs.tf",
        "content": "output \"api_endpoint\" { ... }",
        "language": "hcl"
      }
    ],
    "secrets_setup_instructions": "## Pre-create Secrets\n\nRun these commands...",
    "deployment_instructions": "## Deploy Infrastructure\n\n1. Initialize Terraform..."
  }
}

Response (400 Bad Request):
{
  "error": "Validation failed",
  "details": {
    "is_valid": false,
    "errors": ["Invalid region...", "..."],
    "warnings": []
  }
}
"""
