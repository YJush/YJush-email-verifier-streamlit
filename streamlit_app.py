import streamlit as st
import pandas as pd

# Streamlit UI
st.title("Email List Checker - Duplicate Removal")

st.write("✅ Upload two CSV files with email lists.")
st.write("✅ Checks for duplicate emails between the two lists.")
st.write("✅ Displays and allows downloading of unique emails.")

# File upload
file1 = st.file_uploader("Upload first CSV file", type=["csv"])
file2 = st.file_uploader("Upload second CSV file", type=["csv"])

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Normalize column names to avoid case sensitivity issues
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()

    if 'email' not in df1.columns or 'email' not in df2.columns:
        st.error("CSV files must contain an 'Email' column!")
    else:
        emails1 = set(df1['email'].dropna().str.lower())
        emails2 = set(df2['email'].dropna().str.lower())

        # Check for duplicates
        duplicates = emails1.intersection(emails2)
        unique_emails = emails1.union(emails2) - duplicates

        st.write(f"🔍 Found {len(duplicates)} duplicate emails.")
        st.write(f"📌 Total unique emails: {len(unique_emails)}")

        # Display the unique emails in a dataframe
        df_unique = pd.DataFrame({"Unique Emails": list(unique_emails)})
        st.dataframe(df_unique)

        # Allow download of the unique emails
        csv = df_unique.to_csv(index=False).encode('utf-8')
        st.download_button("Download Unique Emails", data=csv, file_name="unique_emails.csv", mime="text/csv")
