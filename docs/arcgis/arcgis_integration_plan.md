# ArcGIS Integration Plan

## Overview

This document outlines the information and requirements needed to implement ArcGIS publishing functionality for the Green Bond Tracker project. The implementation will allow users to publish green bond data and visualizations to ArcGIS Online or ArcGIS Enterprise.

**Status**: 🚧 NOT YET IMPLEMENTED - Information gathering phase

## Required User Information

Before implementing ArcGIS integration, we need the following information from the user:

### 1. ArcGIS Platform Type

**Question**: Which ArcGIS platform will you use?

- [ ] **ArcGIS Online** (cloud-based SaaS)
- [ ] **ArcGIS Enterprise** (on-premises or private cloud)

**Why we need this**: Different platforms have different API endpoints and authentication mechanisms.

### 2. Organization URL

**Question**: What is your ArcGIS organization URL?

**Examples**:
- ArcGIS Online: `https://myorg.maps.arcgis.com`
- ArcGIS Enterprise: `https://gis.mycompany.com/portal`

**How to find it**:
- ArcGIS Online: Go to your organization's home page
- Enterprise: Contact your GIS administrator

### 3. Authentication Method

**Question**: How do you want to authenticate?

- [ ] **Username/Password** (basic authentication)
- [ ] **OAuth 2.0** (recommended for production)
- [ ] **API Key** (for simple applications)
- [ ] **Integrated Windows Authentication** (Enterprise only)
- [ ] **SAML/Enterprise SSO** (Enterprise only)

**Security considerations**:
- Username/password: Credentials must be stored securely (not in code)
- OAuth 2.0: Requires client ID and client secret
- API Key: Suitable for public read-only access

### 4. Target Folder/Location

**Question**: Where should published items be stored?

- Folder name in your ArcGIS content (e.g., `"Green Bonds"`, `"Sustainability Projects"`)
- Or use root folder (empty string `""`)

**Note**: Folder will be created if it doesn't exist

### 5. Publishing Options

**Question**: What type of ArcGIS items do you want to create?

#### Option A: Feature Service (Recommended)
- [ ] Publish as a **hosted feature service**
  - Allows for querying, editing, and analysis
  - Supports web maps and apps
  - Can be updated incrementally

#### Option B: Web Map
- [ ] Publish as a **web map**
  - Pre-configured visualization
  - Ready to embed in apps or dashboards
  - Can include basemaps and symbology

#### Option C: Both
- [ ] Publish both feature service and web map

### 6. Feature Service Configuration

If publishing a feature service, specify:

**Service name**: `___________________________` (e.g., `"GreenBonds_2024"`)

**Layer name**: `___________________________` (e.g., `"Green Bond Issuance by Country"`)

**Update behavior**:
- [ ] **Overwrite** existing service (replace all data)
- [ ] **Append** to existing service (add new records)
- [ ] **Create new** with timestamp (e.g., `GreenBonds_2024_01_15`)

**Sharing/Permissions**:
- [ ] Private (only you)
- [ ] Organization (all org members)
- [ ] Everyone (public)
- [ ] Specific groups: `___________________________`

### 7. Metadata and Tags

**Title**: `___________________________` (e.g., `"Educational Green Bond Dataset"`)

**Summary**:
```
___________________________________________________________________
___________________________________________________________________
```

**Description**:
```
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
```

**Tags** (comma-separated):
```
___________________________________________________________________
```
Example: `green bonds, sustainability, finance, education, GIS`

**Credits/Attribution**:
```
___________________________________________________________________
```

### 8. Data Synchronization

**Question**: How should data be synchronized?

- [ ] **One-time push** (manual upload)
- [ ] **Scheduled updates** (daily/weekly/monthly)
- [ ] **On-demand refresh** (via CLI command)
- [ ] **Real-time updates** (requires webhook setup)

**Frequency** (if scheduled): `___________________________`

### 9. Geometry/Symbology Preferences

**Geometry type**:
- [ ] Polygon (country boundaries - recommended)
- [ ] Point (country centroids)
- [ ] Both

**Symbology**:
- [ ] Use default ArcGIS styling
- [ ] Apply custom symbology (specify color ramp, classification method)
  - Color ramp: `___________________________` (e.g., `YlGn`, `Blues`)
  - Classification: `___________________________` (e.g., `Natural Breaks`, `Quantile`, `Equal Interval`)
  - Number of classes: `___________________________`

### 10. Advanced Options (Optional)

**Enable time support**:
- [ ] Yes - Enable time series visualization
  - Time field: `issue_date` or `maturity_date`
  - Time interval: `___________________________`

**Enable attachments**:
- [ ] Yes - Allow file attachments to features

**Enable editing**:
- [ ] Yes - Allow users to edit data (not recommended for reference data)

**Custom item ID** (if updating existing):
- Item ID: `___________________________`

## Technical Requirements

### Python Dependencies

The following packages will be required for ArcGIS integration:

```python
arcgis>=2.0.0          # ArcGIS Python API
keyring>=24.0.0        # Secure credential storage (optional)
python-dotenv>=1.0.0   # Environment variable management
```

### Environment Variables (for authentication)

Users will need to set these environment variables or store in a `.env` file:

```bash
# For ArcGIS Online
ARCGIS_URL=https://myorg.maps.arcgis.com
ARCGIS_USERNAME=myusername
ARCGIS_PASSWORD=********  # or use keyring

# For OAuth
ARCGIS_CLIENT_ID=************
ARCGIS_CLIENT_SECRET=************

# For API Key
ARCGIS_API_KEY=************
```

**Security note**: Never commit `.env` file to version control. It's already in `.gitignore`.

## Implementation Plan

### Phase 1: Basic Publishing (v0.3)
- [ ] Implement connection to ArcGIS Online/Enterprise
- [ ] Publish feature service from green bonds data
- [ ] Basic metadata and tagging
- [ ] Overwrite-only update mode

### Phase 2: Enhanced Features (v0.4)
- [ ] Support for incremental updates (append mode)
- [ ] Web map creation with pre-configured symbology
- [ ] Scheduled publishing
- [ ] Better error handling and logging

### Phase 3: Advanced Features (v0.5+)
- [ ] Time-enabled feature services
- [ ] Dashboard creation
- [ ] Notebook publishing
- [ ] Integration with ArcGIS Pro

## CLI Commands (Planned)

```bash
# One-time setup
greenbond arcgis setup

# Publish data
greenbond arcgis publish --mode overwrite

# Update existing service
greenbond arcgis update --service-id ITEM_ID

# List published items
greenbond arcgis list

# Delete published item
greenbond arcgis delete --service-id ITEM_ID
```

## Example Usage (Planned)

```python
from src.arcgis_publisher import ArcGISPublisher

# Initialize publisher
publisher = ArcGISPublisher(
    url="https://myorg.maps.arcgis.com",
    username="myuser",
    password="mypass"  # Or use environment variable
)

# Publish feature service
service = publisher.publish_feature_service(
    data_path="data/green_bonds.csv",
    geo_path="data/countries_geo.json",
    title="Green Bond Issuance by Country",
    tags=["green bonds", "sustainability"],
    folder="Green Bonds",
    share_level="organization"
)

print(f"Published service: {service.url}")
print(f"Item ID: {service.id}")
```

## Testing Without ArcGIS Credentials

The test suite must work without ArcGIS credentials. Tests for ArcGIS functionality will:

1. **Mock external API calls** using `unittest.mock`
2. **Skip tests if credentials unavailable** using `@pytest.mark.skipif`
3. **Use dummy/sample data** instead of live ArcGIS services

Example:
```python
@pytest.mark.skipif(
    not os.getenv("ARCGIS_USERNAME"),
    reason="ArcGIS credentials not available"
)
def test_arcgis_publishing():
    # This test only runs if ARCGIS_USERNAME is set
    pass
```

## Resources and Documentation

- [ArcGIS Python API Documentation](https://developers.arcgis.com/python/)
- [Publishing Feature Services](https://developers.arcgis.com/python/guide/working-with-feature-layers-and-features/)
- [Authentication Guide](https://developers.arcgis.com/python/guide/working-with-different-authentication-schemes/)
- [Best Practices](https://developers.arcgis.com/python/guide/best-practices/)

## Questions?

If you have questions about ArcGIS integration, please:

1. Review the [ArcGIS Python API documentation](https://developers.arcgis.com/python/)
2. Check your organization's ArcGIS administrator policies
3. Open an issue on GitHub with your questions
4. Tag the issue with `arcgis` label

## Disclaimer

This integration is for **educational purposes only**. Please ensure:

- You have proper licenses for ArcGIS Online/Enterprise
- You comply with your organization's data governance policies
- You do not publish sensitive or proprietary data publicly
- You understand the cost implications of data storage and service hosting

---

**Document Version**: 1.0
**Last Updated**: 2024-12-30
**Status**: Awaiting user input for implementation
