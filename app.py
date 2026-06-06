import streamlit as st
import pandas as pd
import urllib.parse

# Page Title
st.set_page_config(page_title="Faculty Email Generator")

st.title("📧 Faculty Email Draft Generator")

# Upload File
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        # Search Box
        search_name = st.text_input("🔍 Search Faculty Name")

        if search_name:
            df = df[
                df["Faculty Name"].str.contains(
                    search_name,
                    case=False,
                    na=False
                )
            ]

        st.success("Excel file uploaded successfully!")
        if st.button("Generate Email Drafts"):

            for index, row in df.iterrows():

                faculty = str(row["Faculty Name"])
                department = str(row["Department"])
                topic = str(row["Topic"])
                date = str(row["Date"])
                time = str(row["Time"])
                venue = str(row["Venue"])
                email = str(row["Email"])

                subject = "Training Session Notification"

                st.divider()

                st.subheader(f"📄 Draft for {faculty}")

                st.write(f"**To:** {email}")
                st.write(f"**Subject:** {subject}")

                st.write("")
                st.write(f"Dear {faculty},")
                st.write("")
                st.write(
                    "You are requested to attend the following training session:"
                )

                # REAL TABLE
                table_df = pd.DataFrame({
                    "Faculty Name": [faculty],
                    "Department": [department],
                    "Topic": [topic],
                    "Date": [date],
                    "Time": [time],
                    "Venue": [venue]
                })

                st.table(table_df)

                st.write("")
                st.write("Kindly attend the session as scheduled.")
                st.write("")
                st.write("Regards,")
                st.write("HR Department")

                # Gmail Body
                email_body = f"""
Dear {faculty},

You are requested to attend the following training session.

Faculty Name: {faculty}
Department: {department}
Topic: {topic}
Date: {date}
Time: {time}
Venue: {venue}

Kindly attend the session as scheduled.

Regards,
HR Department
"""

                gmail_link = (
                    "https://mail.google.com/mail/?view=cm&fs=1"
                    f"&to={urllib.parse.quote(email)}"
                    f"&su={urllib.parse.quote(subject)}"
                    f"&body={urllib.parse.quote(email_body)}"
                )

                st.link_button(
                    "📨 Open in Gmail",
                    gmail_link
                )

    except Exception as e:
        st.error(f"Error: {e}")