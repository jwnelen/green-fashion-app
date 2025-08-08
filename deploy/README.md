# Deployment Guide

This document describes how to deploy the Green Fashion API to Google Cloud Platform.

## Overview

The deployment uses:
- **Google Cloud Run** for hosting the FastAPI application
- **Google Cloud Storage** for image storage
- **MongoDB Atlas** or self-hosted MongoDB for data storage
- **Google Secret Manager** for secure configuration

## Quick Start

### 1. Local Development

```bash
# Run locally with Docker Compose
./deploy/scripts/local-deploy.sh
```

This will start:
- FastAPI server at `http://localhost:8000`
- API documentation at `http://localhost:8000/docs`
- MongoDB at `mongodb://localhost:27017`
- MongoDB Admin UI at `http://localhost:8081` (optional)

### 2. Cloud Deployment

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform (first time only)
terraform init

# Plan deployment
terraform plan -var-file="environments/dev.tfvars"

# Deploy to development
terraform apply -var-file="environments/dev.tfvars"

# Deploy to production
terraform apply -var-file="environments/prod.tfvars"
```

## Configuration

### Environment Variables

Required environment variables:
- `MONGODB_URI` - MongoDB connection string
- `GCS_PROJECT_ID` - Google Cloud Project ID
- `GCS_BUCKET_DEV` - Development storage bucket
- `GCS_BUCKET_PROD` - Production storage bucket

### Secrets Management

Secrets are managed through Google Secret Manager:
- `mongodb-uri` - MongoDB connection string
- `gcs-service-account-key` - GCS service account credentials (dev only)

### Build Context

The API is built using the Dockerfile in the `api/` folder with the project root as build context, allowing access to the `green_fashion/` package.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Cloud Storage  │    │   MongoDB       │
│   (FastAPI)     │◄──►│   (Images)       │    │   (Data)        │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │  Secret Manager  │
                    │  (Configuration) │
                    └──────────────────┘
```

## Monitoring

The deployment includes:
- Health checks at `/health`
- Startup and liveness probes
- Logging and monitoring through Google Cloud Operations

## API Endpoints

Once deployed, the API provides:
- `GET /health` - Health check
- `GET /items` - List all clothing items
- `POST /items` - Create new item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item
- `GET /docs` - OpenAPI documentation

## Troubleshooting

### Common Issues

1. **Build failures**: Ensure all dependencies are in `pyproject.toml`
2. **MongoDB connection**: Check `MONGODB_URI` secret in Secret Manager
3. **Storage issues**: Verify GCS service account permissions
4. **Health check failures**: Check application logs in Cloud Run

### Useful Commands

```bash
# View Cloud Run logs
gcloud run services logs read green-fashion-dev --region=us-central1

# Update secrets
gcloud secrets versions add mongodb-uri --data-file=-

# Force new deployment
gcloud run services update green-fashion-dev --region=us-central1
```
