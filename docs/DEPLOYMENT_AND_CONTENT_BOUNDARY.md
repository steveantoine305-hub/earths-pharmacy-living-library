# DEPLOYMENT AND CONTENT BOUNDARY

This document defines the architecture for separating public website content from internal drafts and future protected subscriber content.

## 1. Deployment Boundary
The Earth’s Pharmacy uses an **Allowlist Deployment Policy**. Only explicitly approved files and directories are published to the public web.

### Public Deployable Source
- **Landing Pages**: `index.html`, `founders-edition/index.html`, `living-library/index.html`, `monographs/index.html`, `safety/index.html`, `about/index.html`.
- **Assets**: `/assets/`, public images.
- **Public Metadata**: `data/library/metadata.json`.

### Internal Content Source (`content/internal/`)
- **DRAFT Monographs**: All monographs currently in production.
- **Production Infrastructure**: Templates, internal notes, and source-review materials.
- **Status**: Never deployed to the public web.

### Future Protected Source (`content/protected/`)
- **Subscriber Content**: Detailed evidence tables, preparation guidance, and citation mapping.
- **Access Control**: Requires a future secure backend for authorized delivery.

## 2. Governance Rules
### Lifecycle Rules
- **DRAFT / SOURCE_REVIEW / QA**: Internal only. Never deployed.
- **READY_FOR_FOUNDER_REVIEW**: Internal only. Never deployed.
- **FOUNDER_APPROVED**: Eligible for public deployment, but requires an explicit publication rule.

### Access-Level Rules
- **public**: Available to all visitors.
- **metered**: Limited free views (Future).
- **subscriber**: Full access for paid accounts (Future).

**Note**: A record can be `FOUNDER_APPROVED` but remain `subscriber` access. Lifecycle status and access level are independent concepts.

## 3. Safety Exception
Critical safety information (toxicity, pregnancy contraindications, emergency warnings) is prioritized for **Public Visibility**. Commercial access levels must never suppress a critical safety warning.

## 4. Deployment Validation
The project includes an automated check (`scripts/validate-deployment.py`) that prevents the accidental publication of DRAFT content. This script must be run before any deployment to GitHub Pages.

## 5. Future Backend Integration
GitHub Pages serves the public discovery layer. Future protected content will be migrated to a secure serverless or containerized backend that verifies user entitlements (subscription or book-buyer status) before serving full records.
