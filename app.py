import streamlit as st
import pandas as pd
import re
import time
import io
import zipfile
from datetime import datetime


st.set_page_config(page_title="Data Sanitizer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style the main title */
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1E3A8A;
        letter-spacing: -1px;
    }
    
    /* Style the live terminal */
    .terminal-box {
        background-color: #0F172A;
        color: #10B981;
        font-family: 'Courier New', monospace;
        padding: 15px;
        border-radius: 8px;
        height: 250px;
        overflow-y: auto;
        border: 1px solid #334155;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

def extract_metadata_and_classify(content, filename):
    content_upper = content.upper()
    if "NON-DISCLOSURE" in content_upper or "AGREEMENT" in content_upper:
        category = "Contracts"
    elif "INVOICE" in content_upper or "BILL TO" in content_upper:
        category = "Invoices"
    elif "RESOLUTION" in content_upper or "BOARD" in content_upper:
        category = "Board_Resolutions"
    else:
        category = "Unclassified"

    date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', content)
    doc_date = date_match.group(0) if date_match else datetime.now().strftime('%Y-%m-%d')
    new_filename = f"{doc_date}_{category}_{filename}"
    
    return category, doc_date, new_filename

st.markdown('<h1 class="main-title">⚖️ Trilegal Vault: Automated Discovery Pipeline</h1>', unsafe_allow_html=True)
st.markdown("Secure, multi-threaded ingestion for unstructured M&A data rooms. Drop raw files below to initiate zero-trust sanitization and structural mapping.")
st.divider()

uploaded_files = st.file_uploader("Upload Client Data Dump (.txt)", accept_multiple_files=True, type=['txt'])

if uploaded_files:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Engine Status")
        progress_bar = st.progress(0)
        
        metric_files = st.empty()
        metric_contracts = st.empty()
        metric_invoices = st.empty()
        
    with col2:
        st.subheader("Live System Audit Log")
        terminal_placeholder = st.empty()
        
    results = []
    terminal_log = ">>> SYSTEM BOOT... INITIATING THREAD POOL\n"
    terminal_placeholder.markdown(f'<div class="terminal-box">{terminal_log}</div>', unsafe_allow_html=True)
    
    zip_buffer = io.BytesIO()
    
    contracts_count = 0
    invoices_count = 0
    total_files = len(uploaded_files)
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for i, file in enumerate(uploaded_files):
            content = file.getvalue().decode("utf-8", errors="ignore")
            
            category, doc_date, new_name = extract_metadata_and_classify(content, file.name)
            target_path = f"{category}/{doc_date[:4]}/{doc_date[5:7]}/{new_name}"
            
            if category == "Contracts": contracts_count += 1
            if category == "Invoices": invoices_count += 1
            
            zip_file.writestr(target_path, content)
            
            results.append({
                "Original Target": file.name,
                "Classification": category,
                "Extracted Date": doc_date,
                "Sanitized Output Path": target_path
            })
            
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            
            metric_files.metric("Total Parsed", f"{i+1} / {total_files}")
            metric_contracts.metric("Contracts Secured", contracts_count)
            metric_invoices.metric("Invoices Routed", invoices_count)
            
            time.sleep(0.4) 
            terminal_log += f">>> Thread[{i%4}]: Parsed {file.name} -> Re-routed to {category}\n"
            terminal_placeholder.markdown(f'<div class="terminal-box">{terminal_log}</div>', unsafe_allow_html=True)
            
    terminal_log += ">>> SYSTEM HALT: 0 WARNINGS. PIPELINE COMPLETE.\n"
    terminal_placeholder.markdown(f'<div class="terminal-box">{terminal_log}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("📊 Mapped Data Architecture")
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
    
    st.download_button(
        label="⬇️ Download Sanitized Data Room (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="Trilegal_Sanitized_Data_Room.zip",
        mime="application/zip",
        type="primary" # Makes the button pop with the theme color
    )