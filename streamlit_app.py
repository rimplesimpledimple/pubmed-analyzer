import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote
from io import StringIO

# Set page config
st.set_page_config(
    page_title="Paper Analysis Tool",
    page_icon="📚",
    layout="wide"
)

# Constants
API_BASE_URL = "http://localhost:8000"

# Title and description
st.title("📚 Paper Analysis Tool")
st.markdown("Enter a paper URL to analyze its content, get a summary, and view extracted tables.")

# Input URL
url = st.text_input("Enter Paper URL", placeholder="https://pubmed.ncbi.nlm.nih.gov/...")

if url:
    # Create tabs for different views
    tab_analysis, tab_download = st.tabs(["Full Analysis", "Download Paper"])
    
    with tab_analysis:
        try:
            # Make API call to analysis endpoint
            response = requests.post(
                f"{API_BASE_URL}/get-analysis",
                json={"url": url}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Create two columns for metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Paper Details")
                    st.write(f"**Title:** {data['metadata']['title']}")
                    st.write(f"**Paper ID:** {data['paper_id']}")
                    st.write(f"**Source URL:** {data['metadata']['url']}")
                
                with col2:
                    st.subheader("Abstract")
                    st.write(data['metadata']['abstract'])
                
                # Display summary
                st.subheader("Summary")
                st.write(data['summary'])
                
                # Display table if available
                if data.get('main_table'):
                    st.subheader("Main Table")
                    st.info(data['main_table']['description'])
                    
                    try:
                        # Convert CSV string to DataFrame using StringIO from io module
                        df = pd.read_csv(StringIO(data['main_table']['csv_content']))
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        if data['main_table']['footnotes']:
                            st.caption("**Table Footnotes:**")
                            st.caption(data['main_table']['footnotes'])
                    except Exception as e:
                        st.error(f"Error displaying table: {str(e)}")
                else:
                    st.info("No table data available for this paper.")
                    
            else:
                # Handle error responses based on exceptions.py structure
                try:
                    error_data = response.json()
                    # UserFacingError messages can be shown directly to users
                    st.error(error_data.get('error', 'An unknown error occurred'))
                except ValueError:
                    # If response isn't JSON, show generic error
                    st.error(f"Server error (Status code: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the backend server. Make sure the FastAPI server is running on port 8000.")
        except requests.exceptions.RequestException as e:
            st.error("Failed to communicate with the server. Please try again later.")
        except Exception as e:
            st.error("An unexpected error occurred. Please try again later.")
    
    with tab_download:
        try:
            st.subheader("Download Paper")
            encoded_url = quote(url, safe='')
            response = requests.get(f"{API_BASE_URL}/papers/{encoded_url}/download")
            
            if response.status_code == 200:
                # Provide download button
                st.download_button(
                    label="Download PDF",
                    data=response.content,
                    file_name=f"paper_{encoded_url.split('/')[-1]}.pdf",
                    mime="application/pdf"
                )
            else:
                # Handle error responses based on exceptions.py structure
                try:
                    error_data = response.json()
                    st.error(error_data.get('error', 'Failed to download the paper'))
                except ValueError:
                    st.error(f"Download failed (Status code: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            st.error("Failed to download the paper. Please check your connection and try again.")
        except Exception as e:
            st.error("An unexpected error occurred while downloading the paper.") 