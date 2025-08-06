# GitHub Actions Workflows

This project uses a separated workflow approach for better efficiency and control.

## 🔧 Active Workflows

### 1. **CI Pipeline** (`ci.yml`)
- **Triggers**: All PRs and pushes to main
- **Purpose**: Run tests, security scans, and basic Docker builds
- **What it does**:
  - Python tests with pytest
  - Code quality checks (black, isort, flake8, mypy)
  - Security scanning (bandit, safety)
  - Docker build testing

### 2. **Build and Push** (`build-and-push.yml`)
- **Triggers**: Code changes in application files
  ```
  - green_fashion/**
  - streamlit_app/**
  - Dockerfile
  - requirements.txt
  - pyproject.toml
  - .dockerignore
  ```
- **Purpose**: Build and push Docker images when application code changes
- **What it does**:
  - Builds Docker images with proper tagging
  - Pushes to Google Container Registry
  - Runs container smoke tests on PRs
  - Uses build cache for efficiency

### 3. **Deploy Infrastructure** (`deploy-infrastructure.yml`)
- **Triggers**: Infrastructure changes or manual dispatch
  ```
  - terraform/**
  - .github/workflows/deploy-infrastructure.yml
  ```
- **Purpose**: Deploy infrastructure changes using Terraform
- **What it does**:
  - Determines target environment (dev/staging/prod)
  - Gets latest available container image
  - Runs Terraform plan/apply
  - Performs health checks
  - Supports manual deployment with custom images

## 🎯 Workflow Triggers

| Event | Build & Push | Deploy Infrastructure |
|-------|-------------|----------------------|
| Code change in `green_fashion/` | ✅ | ❌ |
| Code change in `streamlit_app/` | ✅ | ❌ |
| Dockerfile change | ✅ | ❌ |
| Terraform change | ❌ | ✅ |
| Push to `develop` | ✅ (if code changed) | ✅ (if infra changed) |
| Push to `main` | ✅ (if code changed) | ✅ (if infra changed) |
| Manual trigger | ❌ | ✅ |

## 🚀 Deployment Flow

### Automatic Deployment
1. **Code Change**: Push to `develop` or `main`
2. **Build**: If app code changed → Build & Push runs
3. **Deploy**: If Terraform changed → Deploy Infrastructure runs
4. **Result**: Latest image deployed with latest infrastructure

### Manual Deployment
1. **Trigger**: Use "Deploy Infrastructure" workflow dispatch
2. **Choose**: Environment (dev/staging/prod)
3. **Optional**: Specify custom container image
4. **Deploy**: Infrastructure deploys with chosen image

## 📂 Environment Mapping

- `develop` branch → `dev` environment
- `main` branch → `prod` environment
- Manual dispatch → Choose any environment

## 🔐 Required Secrets

- `GCP_PROJECT_ID`: Google Cloud Project ID
- `GCP_CREDENTIALS`: Service account JSON key
- `MONGODB_URI`: MongoDB connection string

## 🏷️ Image Tagging Strategy

Images are tagged with:
- `latest` (default branch only)
- `{branch-name}-{sha}` (all builds)
- `pr-{number}` (pull requests)

## ⚠️ Deprecated Workflows

- `deploy-dev.yml` - Use separated workflows instead
- `deploy-prod.yml` - Use separated workflows instead

## 💡 Benefits

✅ **Efficiency**: Only rebuild when code changes
✅ **Speed**: Infrastructure-only changes deploy faster
✅ **Control**: Deploy any image to any environment
✅ **Caching**: Docker layers cached between builds
✅ **Flexibility**: Independent control of build and deploy
