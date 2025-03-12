import streamlit as st
import pandas as pd
import re
import dns.resolver
import smtplib


# Function to validate email syntax
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)


# Function to check MX records
def check_mx_record(email):
    try:
        domain = email.split('@')[-1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        return bool(mx_records)
    except:
        return False


# Function to check SMTP authentication
def check_smtp(email):
    try:
        domain = email.split('@')[-1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)

        server = smtplib.SMTP(mx_record, 25, timeout=5)
        server.helo()
        server.mail('you@example.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False


# Streamlit UI
st.title("Email List Checker and Verifier")

st.write("✅ Upload two CSV files with email lists.")
st.write("✅ Checks for duplicate emails between the two lists.")
st.write("✅ Performs email verification, including:")
st.write("- Syntax check (ensures valid email format)")
st.write("- MX record check (confirms the domain can receive emails)")
st.write("- SMTP authentication (checks if the email actually exists)")
st.write("✅ Displays valid emails after filtering out duplicates and invalid ones.")
st.write("✅ Allows downloading of verified emails.")

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
        st.write(f"📌 Total unique emails to verify: {len(unique_emails)}")

        valid_emails = []
        invalid_emails = []

        for email in unique_emails:
            syntax_valid = is_valid_email(email)
            mx_valid = check_mx_record(email) if syntax_valid else False
            smtp_valid = check_smtp(email) if mx_valid else False

            if syntax_valid and mx_valid and smtp_valid:
                valid_emails.append(email)
            else:
                invalid_emails.append({
                    "Email": email,
                    "Syntax": syntax_valid,
                    "MX Record": mx_valid,
                    "SMTP": smtp_valid
                })

        # Display results
        st.write(f"✅ Valid emails ready to send: {len(valid_emails)}")
        st.write(f"❌ Invalid emails found: {len(invalid_emails)}")

        if invalid_emails:
            st.write("### ❌ Invalid Email Breakdown")
            df_invalid = pd.DataFrame(invalid_emails)
            st.dataframe(df_invalid)

        if valid_emails:
            df_valid = pd.DataFrame({"Valid Emails": valid_emails})
            st.dataframe(df_valid)

            # Allow download of valid emails
            csv = df_valid.to_csv(index=False).encode('utf-8')
            st.download_button("Download Verified Emails", data=csv, file_name="verified_emails.csv", mime="text/csv")
