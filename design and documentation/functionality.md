# Streamlit Data Catalog Application Design

## Overview
This plan outlines the design and implementation of a Streamlit application that replicates the data catalog interface shown in the mockup.

## Key Components Analysis

### 1. Main Screen Layout
- **Header**: "Main Screen" title
- **Search Bar**: "Search for a table or data catalog" functionality
- **Advanced Filters**: Collapsible/expandable filter section
- **Catalog Cards**: Grid layout (3 columns)showing different data catalogs

#### Mockup
![Mockup](/mockups/Keboola_Data_Catalog-main.png)

### 2. Card Information Structure
Each catalog card contains:
- Title/Name
- Owner field
- Last Change date
- Number of Tables count
- Description text area
- Details button

### 3. Search Functionality
- Text input for searching catalogs 
- Real-time filtering based on catalog name, description, tags or owner
- Same logic applies for values in tables list (name, description, tags)
- Search across multiple fields (name, description, tags, owner)


### 4. Advanced Filters
- Dedicated filters for catalog and table properties 
- Real-time filtering
- Catalog filters:
    - catalog name (text filter)
    - catalog description (text filter)
    - Catalog tags (pre-generated multiselect)
    - Catalog owner (pre-generated multiselect)
    - Catalog Maturity (pre-generated multiselect)
- Table filters:
    - table name (text filter)
    - Table description (text filter)
    - Table tags (pre-generated multiselect)

#### Mockup
![Mockup](/mockups/Keboola_Data_Catalog-search_filters.png)

### 5. Catalog Details (popup)
Each catalog detail contains:
- Title/Name
- Owner field
- Maturity
- Number of Tables count
- Description text area
- Tables list with columns:
  - Name
  - Description
  - Last Modified date
  - Number of rows
- Request Access area (Collapsible/expandable section)

#### Mockup
![Mockup](/mockups/Keboola_Data_Catalog-detail.png)

### 6. Request Access area (Collapsible/expandable section)
Section contains those fields:
 - Reason for request
 - requestor email
 - send request button

#### Mockup
![Mockup](/mockups/Keboola_Data_Catalog-request_access.png)

## UI elements behaviour:
- When user clicks on the "Details" button, the popup with catalog details is opened
- When user clicks on the "Request Access" button, the popup with request access form is opened
- When user clicks on the "Close" button, the popup is closed
- When user clicks on the "Send Request" button, the request is sent to the owner of the catalog
- When user clicks on the "Close" button, the popup is closed
- When user searches in the search field, the search results are displayed in the catalog cards
- When user clicks on the "Advanced Filters" button, the advanced filters are opened
- When user clicks types in the filters that are text fields, the search results are displayed in the catalog cards
- When user clicks types in the filters that are multiselect fields, the search results are displayed in the catalog cards
- When user clicks types in the filters that are multiselect fields, the search results are displayed in the catalog cards

## Streamlit Implementation Plan

### 1. Application Structure
```
streamlit_data_catalog/
├── app.py                 # Main application file
├── components/
│   ├── catalog_card.py    # Reusable catalog card component
│   ├── search_filter.py   # Search and filter functionality
│   └── data_manager.py    # Data handling and management
├── data/
│   └── catalogs.json      # Sample catalog data
├── styles/
│   └── custom.css         # Custom styling
└── requirements.txt       # Dependencies
```

### 2. Core Features to Implement

#### Search Functionality
- Text input for searching catalogs
- Real-time filtering based on catalog name, description, or owner
- Search across multiple fields (name, description, tags, owner)

#### Advanced Filters
- Expandable filter section using `st.expander()`
- Filter by:
  - Name
  - Description
  - Tags
  - Owner

#### Catalog Cards
- Custom styled cards using `st.container()` and CSS
- Color-coded based on maturity (green for certified, red for development)
- Responsive grid layout using Streamlit columns
- Interactive "Details" buttons that trigger popup modals with catalog information

##### Catalog Maturity (sorted categories) - logic
- **Certified Data Catalogs** (Green cards)
  - This is based on the data "color" field ('#07BE07': 'Certified')
- **Under Development** (Red cards)
  - This is based on the data "color" field ('#FF5B50': 'Development')

#### Data Management
- JSON/CSV file to store catalog metadata
- Read-only data loading on application startup
- State management for filters and search

### 3. Technical Implementation Details

#### Layout Strategy
- Use `st.columns()` for responsive grid layout
- Implement custom CSS for card styling
- Use `st.container()` for each catalog card
- Responsive design that adapts to screen size

#### Styling Approach
- Custom CSS for card appearance
- Color scheme matching the mockup (green for certified, red for development)
- Hover effects and interactive elements
- Consistent spacing and typography

#### State Management
- Session state for maintaining filter selections
- Search query persistence
- Modal state management for popup displays
- Access request form state handling

### 4. Data Structure

#### Secrets.toml structure
Example:
```
stack_url = "https://connection.north-europe.azure.keboola.com/"
organization_id = "544"
manage_token = "XXXXX-XXXXXXXXXXX"
``` 

#### API calls variables
 - {stack_url} = {BASE_URL}) (for example: https://connection.keboola.com/ or https://connection.us-east4.gcp.keboola.com)
 - {organization_id} - ID of target Keboola organization
 - {storage_token} = {STORAGE_API_TOKEN} (for example: XXX-XXXXX-XXXXXXXXXXXXXXXXX")
 - {manage_token} = {MANAGE_API_TOKEN} (for example: XXX-XXXXX-XXXXXXXXXXXXXXXXX")

 Note: Application will be using majority of those variables from secrets.toml file, unless they are variables resulting from previous API calls.

#### Incoming data structure from API - List Projects in the organization
[API call](https://keboolamanagementapi.docs.apiary.io/#reference/projects/organization-projects/list-projects-for-an-organization)   

Call example:   
```
curl --include \
     --header "Content-Type: application/json" \
     --header "X-KBC-ManageApiToken: XXX-XXXXX-XXXXXXXXXXXXXXXXX" \
  '{BASE_URL}/manage/organizations/{organization_id}/projects'
```

Response:
```python
{
  "id": 101,
  "name": "test project",
  "type": "production",
  "region": "eu-west-1",
  "created": "2017-02-15T14:25:15+0100",
  "expires": null,
  "features": [
    "featureName"
  ],
  "dataSizeBytes": 49152,
  "rowsCount": 200,
  "hasMysql": false,
  "hasRedshift": false,
  "hasSynapse": false,
  "hasExasol": false,
  "hasTeradata": false,
  "hasSnowflake": true,
  "defaultBackend": "snowflake",
  "hasTryModeOn": "0",
  "limits": {
    "limitName": {
      "name": "limitName",
      "value": 10
    }
  },
  "metrics": {},
  "isDisabled": false,
  "billedMonthlyPrice": null,
  "dataRetentionTimeInDays": 1,
  "fileStorageProvider": "aws"
}
```

#### Incoming data structure from API - List Buckets
[API call](https://keboola.docs.apiary.io/#reference/buckets/create-or-list-buckets/list-all-buckets)   

Call example:   
```
curl --include \
     --header "X-StorageApi-Token: XXX-XXXXX-XXXXXXXXXXXXXXXXX" \
  '{BASE_URL}/v2/storage/buckets?include=metadata,linkedBuckets'
```

Response:
```python
{
{
        "id": "in.c-northwind_dataset",
        "name": "c-northwind_dataset",
        "displayName": "northwind_dataset",
        "stage": "in",
        "description": "",
        "sharing": "organization",
        "created": "2024-02-12T22:53:23+0100",
        "lastChangeDate": "2024-11-20T04:22:47+0100",
        "dataSizeBytes": 99840,
        "rowsCount": 3362,
        "backend": "snowflake",
        "hasExternalSchema": false,
        "databaseName": "",
        "path": "in.c-northwind_dataset",
        "project": {
            "id": 7167,
            "name": "Keboola Sandbox (Fisa)"
        },
        "tables": [
            {
                "id": "in.c-northwind_dataset.CATEGORIES",
                "name": "CATEGORIES",
                "displayName": "CATEGORIES",
                "path": "/122973-CATEGORIES"
            },
            {
                "id": "in.c-northwind_dataset.CUSTOMERS",
                "name": "CUSTOMERS",
                "displayName": "CUSTOMERS",
                "path": "/122973-CUSTOMERS"
            },
            {
                "id": "in.c-northwind_dataset.CUSTOMER_DEMOGRAPHICS",
                "name": "CUSTOMER_DEMOGRAPHICS",
                "displayName": "CUSTOMER_DEMOGRAPHICS",
                "path": "/122973-CUSTOMER_DEMOGRAPHICS"
            },
            {
                "id": "in.c-northwind_dataset.EMPLOYEES",
                "name": "EMPLOYEES",
                "displayName": "EMPLOYEES",
                "path": "/122973-EMPLOYEES"
            },
            {
                "id": "in.c-northwind_dataset.EMPLOYEE_TERRITORIES",
                "name": "EMPLOYEE_TERRITORIES",
                "displayName": "EMPLOYEE_TERRITORIES",
                "path": "/122973-EMPLOYEE_TERRITORIES"
            },
            {
                "id": "in.c-northwind_dataset.ORDERS",
                "name": "ORDERS",
                "displayName": "ORDERS",
                "path": "/122973-ORDERS"
            },
            {
                "id": "in.c-northwind_dataset.ORDER_DETAILS",
                "name": "ORDER_DETAILS",
                "displayName": "ORDER_DETAILS",
                "path": "/122973-ORDER_DETAILS"
            },
            {
                "id": "in.c-northwind_dataset.PRODUCTS",
                "name": "PRODUCTS",
                "displayName": "PRODUCTS",
                "path": "/122973-PRODUCTS"
            },
            {
                "id": "in.c-northwind_dataset.REGION",
                "name": "REGION",
                "displayName": "REGION",
                "path": "/122973-REGION"
            },
            {
                "id": "in.c-northwind_dataset.SHIPPERS",
                "name": "SHIPPERS",
                "displayName": "SHIPPERS",
                "path": "/122973-SHIPPERS"
            },
            {
                "id": "in.c-northwind_dataset.SUPPLIERS",
                "name": "SUPPLIERS",
                "displayName": "SUPPLIERS",
                "path": "/122973-SUPPLIERS"
            },
            {
                "id": "in.c-northwind_dataset.TERRITORIES",
                "name": "TERRITORIES",
                "displayName": "TERRITORIES",
                "path": "/122973-TERRITORIES"
            },
            {
                "id": "in.c-northwind_dataset.US_STATES",
                "name": "US_STATES",
                "displayName": "US_STATES",
                "path": "/122973-US_STATES"
            }
        ],
        "color": "#07BE07",
        "sharingParameters": [],
        "sharedBy": {
            "id": 29151,
            "name": "fisa@keboola.com",
            "date": "2025-06-19T21:39:52+0200"
        },
        "owner": {
            "id": 305,
            "name": "Martin Fiser",
            "email": "fisa@keboola.com"
        }
    },
    ...
}
```

#### Incoming data structure from API - Bucket Tables
[API call](https://keboola.docs.apiary.io/#reference/tables/create-or-list-tables/tables-in-bucket)   

Call example:   
```
curl --include \
     --header "X-StorageApi-Token: XXX-XXXXX-XXXXXXXXXXXXXXXXX" \
  '{BASE_URL}/v2/storage/buckets/{BUCKET_ID}/tables?include=columns,metadata,columnMetadata'
```

Response:
```python
{
    {
        "uri": "https://connection.us-east4.gcp.keboola.com/v2/storage/tables/in.c-discogs-vinyl-collection.collection_items",
        "id": "in.c-discogs-vinyl-collection.collection_items",
        "name": "collection_items",
        "displayName": "collection_items",
        "transactional": false,
        "primaryKey": [
            "release_id"
        ],
        "indexType": null,
        "indexKey": [],
        "distributionType": null,
        "distributionKey": [],
        "syntheticPrimaryKeyEnabled": false,
        "created": "2025-06-03T20:47:42+0200",
        "lastImportDate": "2025-06-03T20:47:48+0200",
        "lastChangeDate": "2025-06-03T20:47:48+0200",
        "rowsCount": 160,
        "dataSizeBytes": 68608,
        "isAlias": false,
        "isAliasable": true,
        "isTyped": false,
        "tableType": "table",
        "path": "/7616-collection_items",
        "columns": [
            "album_title",
            "all_artists",
            "all_formats",
            "all_labels",
            "collection_item_id",
            "cover_image_url",
            "date_added",
            "extraction_date",
            "format_type",
            "genres",
            "instance_id",
            "primary_artist",
            "primary_label",
            "release_id",
            "release_year",
            "styles",
            "thumbnail_url",
            "user_rating",
            "username"
        ],
        "metadata": [
            {
                "id": "971021",
                "key": "KBC.createdBy.component.id",
                "value": "kds-team.app-custom-python",
                "provider": "system",
                "timestamp": "2025-06-03T20:47:48+0200"
            },
            {
                "id": "971022",
                "key": "KBC.createdBy.configuration.id",
                "value": "22379447",
                "provider": "system",
                "timestamp": "2025-06-03T20:47:48+0200"
            },
            {
                "id": "971023",
                "key": "KBC.lastUpdatedBy.component.id",
                "value": "kds-team.app-custom-python",
                "provider": "system",
                "timestamp": "2025-06-03T20:47:48+0200"
            },
            {
                "id": "971024",
                "key": "KBC.lastUpdatedBy.configuration.id",
                "value": "22379447",
                "provider": "system",
                "timestamp": "2025-06-03T20:47:48+0200"
            }
        ],
        "columnMetadata": {}
    },
    ...
}
```


#### Final Catalog Data Model construction

This section describes the logic for constructing the final catalog data model from the incoming data. For instance, field mappings (e.g., how bucket.color maps to catalog.maturity)

 - list of buckets that are shared:
 ```python
 is_shared = bucket.get("sharing") is not None
 ```

 - list of buckets have to be filtered based on this logic:
```python
allowed_colors = {
        '#07BE07': 'Certified',
        '#FF5B50': 'Development'
    }
```

 - fill missing owner with sharedBy fallback:
 ```python
if not bucket.get("owner") and bucket.get("sharedBy"):
    bucket['owner'] = {
        'name': bucket['sharedBy'].get('name'),
        'email': bucket['sharedBy'].get('name')
    }
```

#### Final Catalog Data Model

```python
{
    "id": "unique_identifier",
    "name": "Digital",
    "project_id": "1234567890",
    "project_name": "Keboola Sandbox (Fisa)",
    "maturity": "Certified"/"Development" (based on the color)
    "owner": "John.Doe@keboola.com", (transformed from the shareBy field - 'fill missing owner with sharedBy fallback' section)
    "last_change": "2024-07-10",
    "number_of_tables": 25,
    "description": "Digital analytics and web tracking data",
    "created_date": "2024-01-15",
    "tags": ["analytics", "web", "tracking"] (note: tags will be added later, now use only `"tags": ["catalog"]`)
}
```

#### Suggested API functionality and logic:
- Get list of projects for a given organization
- Generate a temporary storage token for given project
- Get list of buckets for a given project (incl. metadata)
- Get list of tables for a given bucket (including metadata)

```python
def get_projects(manage_token, stack_url, organization_id):
    """Fetch list of projects from Keboola Manage API."""
    headers = {
        'X-KBC-ManageApiToken': manage_token,
        'Content-Type': 'application/json'
    }
    stack_url = stack_url.replace('https://', '').replace('http://', '')
    url = f"https://{stack_url}/manage/organizations/{organization_id}/projects"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_storage_token(manage_token, project_id, stack_url):
    """Generate a temporary storage token for given project."""
    headers = {
        'X-KBC-ManageApiToken': manage_token,
        'Content-Type': 'application/json'
    }
    payload = {
        "description": "Temporary token for data product scan",
        "expiresIn": 3600,
        "canManageBuckets": True,
        "canReadAllFileUploads": True,
        "canManageTokens": False
    }
    stack_url = stack_url.replace('https://', '').replace('http://', '')
    url = f"https://{stack_url}/manage/projects/{project_id}/tokens"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['token']

def get_buckets(storage_token, stack_url):
    """Fetch all buckets for a project."""
    headers = {
        'X-StorageApi-Token': storage_token,
        'Content-Type': 'application/json'
    }
    stack_url = stack_url.replace('https://', '').replace('http://', '')
    url = f"https://{stack_url}/v2/storage/buckets?include=metadata"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
```

### 5. User Experience Features

#### Interactive Elements
- Clickable "Details" buttons that open popup modals
- Sortable columns (by date, name, table count) - not 100% needed, but nice to have
- Modal popup navigation and interaction
- Access request submission functionality

#### Detail Views
- Modal popups triggered by "Details" buttons
- Comprehensive catalog information display
- "Request Access" button for each catalog
- Access request functionality (form with email and reason)


### 6. Advanced Features (Phase 2)

#### Search Enhancements
- Fuzzy search capabilities
- Search suggestions/autocomplete

#### Integration Capabilities
- Notification (email) for access requests
- Audit logging for changes

### 7. Performance Considerations

#### Optimization Strategies
- Pagination for large datasets
- Efficient filtering algorithms

## Implementation Priority

### Phase 1 (MVP)
1. Basic layout and card structure
2. Search functionality
3. Static catalog data display
4. Basic filtering
5. Popup modals for catalog details
6. "Request Access" button functionality

### Phase 2 (Enhanced)
1. Advanced filters
2. Enhanced popup design and information display
3. Access request form and submission
4. Custom styling and animations

### Phase 3 (Advanced)
1. Access request tracking via Keboola platform events (see [Creating Events](https://pypi.org/project/keboola-streamlit/))

## Technical Requirements

### Modal Implementation in Streamlit
- Use st.session_state.modal_state to track modal visibility
- Modal states: 'closed', 'catalog_details', 'access_request'
- Use st.empty() containers for modal content
- Modal triggered by button clicks updating session state

# Example modal state management:
if 'modal_state' not in st.session_state:
    st.session_state.modal_state = 'closed'
    st.session_state.selected_catalog = None

### Error Handling Strategy
- API connection failures: Display user-friendly error messages
- Invalid tokens: Redirect to configuration page
- Empty data: Show "No catalogs found" message
- Rate limiting: Implement exponential backoff
- Network timeouts: 30-second timeout with retry logic

### Dependencies
- `streamlit` - Main framework
- `pandas` - Data manipulation
- `plotly` - Charts and visualizations
- `keboola-streamlit` - [Keboola platform integration](https://pypi.org/project/keboola-streamlit/)

### Deployment Options
- Keboola platform (data app)
Streamlit Cloud (free tier)
- Local development server
