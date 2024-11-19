from datetime import datetime
import os
import time
import streamlit as st
from process_module import Backups_Module # Assuming your method is imported from your module

# Streamlit setup
st.set_page_config(
    layout='wide'
)


# Title of the page
st.title("Backups")

# Create two columns: left for the form, right for the backup log
col1, col2 = st.columns([6, 3])

# log = []
log = []

# Left Column: Form for selecting source dir, backup dir, and interval
with col1:
    st.write("#### Configure your backup settings")

    with st.form(key='backup_form'):
        # Get source directory
        source_dir = st.text_input("Source Directory", "/path/to/source")
        # Get backup directory
        backup_dir = st.text_input("Backup Directory", "/path/to/backup")
        # Get backup interval in minutes
        backup_interval = st.selectbox("Backup Interval", options=["daily", "weekly", "monthly"], index=0)

        # Submit button
        submit_button = st.form_submit_button(label="Start Backup")

        if submit_button:
            backup = Backups_Module(source_dir, backup_dir, backup_interval)
            # Call the run_backup() function from your module
            entry = backup.run_backup()
            log.append(entry)

    # Display the backup log on the right column
    with col2:
        st.write("###### Backup Log")
        for entry in log:
            st.write(entry)
