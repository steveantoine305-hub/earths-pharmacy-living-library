# THE EARTH’S PHARMACY — PAYWALL-READY ARCHITECTURE

This document outlines the technical architecture designed to support a future paid-access model for the Living Evidence Library while maintaining a useful public discovery layer.

## 1. Current Public Architecture
The library currently operates as a static site on GitHub Pages. Publicly accessible files include:
- **Landing Pages**: Home, Safety Center, Founder’s Edition, and Living Evidence Library index.
- **Discovery Layer**: Search and browse interfaces using public metadata.
- **Monographs (Draft)**: Benchmark monographs stored in `/monographs/` (not currently linked for public navigation).

## 2. Future Access Levels
- **Public / Free**: Homepage, Search, Alpha-Index, and top-level metadata (Common Name, Identity, Safety Flags).
- **Metered**: Limited full-monograph access (e.g., 2 free records) for anonymous or registered users.
- **Subscriber**: Unlimited access to the full Living Evidence Library, detailed evidence tables, and preparation guidance.
- **Book-Buyer**: Entitlement for owners of the physical Founder’s Edition.

## 3. Secure Content Delivery
GitHub Pages cannot securely protect content via JavaScript/CSS hiding. To implement a secure paywall, the following transition is required:

### The Integration Boundary
- **Public Layer**: Remains on GitHub Pages (Metadata, Search, Safety Alerts).
- **Protected Layer**: Must move to a secure environment (e.g., a serverless backend or a dedicated web application with authentication).
- **Authentication/Payment Provider**: External services (e.g., Stripe for payments, Auth0 or Firebase for identity) will handle user sessions and entitlement verification.

### Protected Content Requirements
The future system must provide:
1. **Secure User Identity**: Verified login sessions.
2. **Entitlement Verification**: Checking if a user has an active subscription or book-buyer status.
3. **Metered Logic**: Server-side tracking of free views.
4. **Protected Delivery**: Content is only served to authorized sessions, never exposed in public JSON/JS files.

## 4. Public Safety Exception
Critical safety data (Toxicity, Pregnancy Contraindications, Emergency Warnings) is architected to remain **Publicly Visible** even when the detailed monograph is protected. This ensures that the commercial model never suppresses life-saving information.

## 5. Migration Path
1. **Phase II (Current)**: Architecture readiness and metadata separation.
2. **Phase III**: Implementation of a secure backend for monograph delivery.
3. **Phase IV**: Integration of payment and authentication providers.

## 6. Metadata Schema
Public metadata is stored in `data/authority/metadata.json` and includes:
- `access_level`: public, metered, or subscriber.
- `lifecycle_status`: DRAFT, SOURCE_REVIEW, QA, READY_FOR_FOUNDER_REVIEW, FOUNDER_APPROVED.

Website corrections and Living Evidence updates are stored separately from the immutable Revision 2I source copy.
