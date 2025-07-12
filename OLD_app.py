import streamlit as st
import pandas as pd
import json
import time
import requests
import logging
import random
import string
from datetime import datetime

# Streamlit page configuration
st.set_page_config(page_title="Data Products Marketplace", layout="wide")

# ---------------------------
# API FUNCTIONS
# ---------------------------

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

# ---------------------------
# DATA EXTRACTION LOGIC
# ---------------------------

def fetch_keboola_data():
    """Fetch complete Keboola project and bucket structure."""
    manage_token = st.secrets["manage_token"]
    stack_url = st.secrets["stack_url"]
    organization_id = int(st.secrets["organization_id"])

    all_projects_buckets = {}
    projects = get_projects(manage_token, stack_url, organization_id)
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        try:
            storage_token = get_storage_token(manage_token, project_id, stack_url)
            buckets = get_buckets(storage_token, stack_url)
            all_projects_buckets[project_id] = {
                'project_name': project_name,
                'buckets': buckets
            }
        except Exception as e:
            st.error(f"Error fetching buckets for project {project_name}: {e}")
    return all_projects_buckets

def get_shared_dp_buckets(data):
    """Extract shared buckets with specific colors for Data Products."""
    allowed_colors = {
        '#07BE07': 'Production',
        '#FF5B50': 'Development'
    }
    shared_dp_buckets = []
    for project_id, project_data in data.items():
        project_name = project_data.get("project_name", "Unknown")
        for bucket in project_data.get("buckets", []):
            is_shared = bucket.get("sharing") is not None
            color = bucket.get("color")
            if is_shared and color in allowed_colors:
                bucket['maturity'] = allowed_colors[color]
                # Fill missing owner with sharedBy fallback
                if not bucket.get("owner") and bucket.get("sharedBy"):
                    bucket['owner'] = {
                        'name': bucket['sharedBy'].get('name'),
                        'email': bucket['sharedBy'].get('name')
                    }
                bucket_info = {
                    "project_id": project_id,
                    "project_name": project_name,
                    **bucket
                }
                shared_dp_buckets.append(bucket_info)
    return shared_dp_buckets

def extract_kbc_description(bucket):
    """Extract KBC.description from metadata if exists."""
    metadata = bucket.get("metadata", [])
    if isinstance(metadata, list):
        for meta in metadata:
            if meta.get("key") == "KBC.description":
                return meta.get("value")
    return bucket.get("description", "No description available")

# ---------------------------
# STREAMLIT UI COMPONENTS
# ---------------------------

@st.dialog("Data Product Details", width="large")
def show_product_details(row):
    st.subheader(f"[DP] {row['displayName']}")
    owner = row.get("owner", {})
    st.write("### 👤 Owner")
    st.write(f"**Name:** {owner.get('name', 'Unknown')}")
    st.write(f"**Email:** {owner.get('email', 'Unknown')}")
    
    st.write("---")
    st.write("### 🔄 Sharing")
    st.write(f"**Sharing type:** {row.get('sharing', 'N/A')}")
    st.write(f"**Project:** {row.get('project_name', 'Unknown')}")

    st.write("---")
    st.write("### 📊 Tables")
    for table in row.get("tables", []):
        st.write(f"- {table.get('name', 'Unnamed')}")
    
    st.write("---")
    st.write("### ℹ️ Description")
    st.markdown(extract_kbc_description(row))

@st.dialog("Request Access", width="large")
def request_access(row, i):
    st.subheader(f"[DP] {row['displayName']}")
    st.write(f"Send to: {row.get('owner', {}).get('email', 'Unknown')}")

    form_key = f"request_form_{i}"
    if form_key not in st.session_state:
        st.session_state[form_key] = {"submitted": False, "purpose": "", "duration": "1 month"}

    if not st.session_state[form_key]["submitted"]:
        purpose = st.text_area("Purpose of Request:", key=f"purpose_{i}")
        duration = st.selectbox("Access Duration:", ["1 month", "3 months", "6 months", "1 year", "Permanent"], key=f"duration_{i}")

        st.session_state[form_key].update({"purpose": purpose, "duration": duration})

        if st.button("Submit Request", key=f"submit_{i}", type="primary"):
            time.sleep(1)
            request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            st.session_state[form_key].update({"submitted": True, "request_id": request_id, "product_name": row['displayName']})
            st.success("🎉 Request submitted!")
            st.info(f"Request ID: REQ-{request_id}")

# ---------------------------
# MAIN APP LOGIC
# ---------------------------

def main():
    st.markdown("""
    <style>
    .maturity-badge {
        display: inline-block; padding: 0.3em 0.8em; font-weight: 600;
        border-radius: 0.4rem; margin-left: 0.5rem;
    }
    .maturity-production { background-color: #07BE07; color: white; }
    .maturity-development { background-color: #FF5B50; color: white; }
    </style>
    """, unsafe_allow_html=True)

    if 'all_data' not in st.session_state:
        with st.spinner("Fetching data from Keboola..."):
            try:
                st.session_state.all_data = fetch_keboola_data()
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

    st.title("Data Products Marketplace")

    if st.button("🔄 Refresh"):
        with st.spinner("Refreshing data..."):
            st.session_state.all_data = fetch_keboola_data()
            st.success("Data refreshed!")

    data = st.session_state.all_data
    if not data:
        st.warning("No data found.")
        return

    shared_dp_buckets = get_shared_dp_buckets(data)
    if not shared_dp_buckets:
        st.warning("No Data Products found.")
        return

    df = pd.DataFrame(shared_dp_buckets)

    # Filters
    st.subheader("Filters")
    name_filter = st.text_input("Name:", "")
    maturity_filter = st.selectbox("Maturity:", ["All", "Production", "Development"])

    filtered_df = df.copy()
    if name_filter:
        filtered_df = filtered_df[filtered_df['displayName'].str.contains(name_filter, case=False)]
    if maturity_filter != "All":
        filtered_df = filtered_df[filtered_df['maturity'] == maturity_filter]

    st.write(f"Showing {len(filtered_df)} data product(s):")

    cols = st.columns(2, gap="large")
    for i, row in enumerate(filtered_df.to_dict("records")):
        with cols[i % 2]:
            with st.container(border=True):
                maturity_class = "maturity-production" if row['maturity'] == "Production" else "maturity-development"
                st.markdown(f"""
                <div style='font-size: 1.4rem; font-weight: 600; color: #1976D2;'>
                    📦 [DP] {row['displayName']} 
                    <span class='maturity-badge {maturity_class}'>{row['maturity']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.write(f"**Owner:** {row.get('owner', {}).get('name', 'Unknown')}")
                with st.expander("Description"):
                    st.write(extract_kbc_description(row))

                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button("View Details", key=f"details_{i}"):
                        show_product_details(row)
                with btn_cols[1]:
                    if st.button("Request Access", key=f"access_{i}", type="primary"):
                        request_access(row, i)

if __name__ == "__main__":
    main()