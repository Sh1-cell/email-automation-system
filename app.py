import streamlit as st
import pandas as pd
from rapidfuzz import process
from gmail_draft import create_draft


def smart_find_column(df, possible_names, label):
    columns = list(df.columns)

    for col in columns:
        clean_col = str(col).strip().lower().replace("_", " ")
        for name in possible_names:
            clean_name = name.strip().lower().replace("_", " ")
            if clean_col == clean_name:
                return col

    match = process.extractOne(label, columns, score_cutoff=60)
    if match:
        return match[0]

    return columns[0] if columns else None


def clean_date(value):
    try:
        return pd.to_datetime(value).strftime("%d-%b-%Y")
    except:
        return str(value)


def clean_time(value):
    try:
        return pd.to_datetime(value).strftime("%I:%M %p")
    except:
        return str(value)


def create_html_body(name, department, topic, date, time, venue, recipient_type):
    return f"""
    <html>
    <body>

    <p>Dear {name},</p>

    <p>You are requested to attend the following training session:</p>

    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
        <tr>
            <th>{recipient_type}</th>
            <th>Department</th>
            <th>Topic</th>
            <th>Date</th>
            <th>Time</th>
            <th>Venue</th>
        </tr>
        <tr>
            <td>{name}</td>
            <td>{department}</td>
            <td>{topic}</td>
            <td>{date}</td>
            <td>{time}</td>
            <td>{venue}</td>
        </tr>
    </table>

    <br>

    <p>
    Regards,<br>
    HR Department
    </p>

    </body>
    </html>
    """


st.set_page_config(
    page_title="Email Automation System",
    page_icon="📧",
    layout="wide"
)

st.image("Adani_2012_logo.png", width=200)

st.markdown("""
# 📧 Email Automation System
### Training & Communication Management Platform
""")

st.markdown("""
<style>
.stApp {background-color: #FFFFFF;}

h1, h2, h3 {color: #5B2C83;}

.stButton > button {
    background-color: #5B2C83;
    color: white;
    border-radius: 10px;
    padding: 10px 18px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #4A236B;
    color: white;
}

.stLinkButton > a {
    background-color: #5B2C83;
    color: white;
    border-radius: 10px;
    padding: 10px 18px;
    text-decoration: none;
    font-weight: 600;
}

[data-testid="stFileUploader"],
[data-testid="stTextInput"],
[data-testid="stSelectbox"] {
    background-color: #F5F0FA;
    padding: 10px;
    border-radius: 12px;
    border: 1px solid #E0D4F0;
}

th {
    background-color: #5B2C83 !important;
    color: white !important;
}

td {
    background-color: #F5F0FA !important;
}
</style>
""", unsafe_allow_html=True)


if "show_drafts" not in st.session_state:
    st.session_state.show_drafts = False

if "df" not in st.session_state:
    st.session_state.df = None


recipient_type = st.selectbox(
    "Select Recipient Type",
    ["Faculty", "Participants", "Trainers", "Employees", "Custom"]
)

if recipient_type == "Custom":
    recipient_type = st.text_input("Enter Custom Heading", value="Recipient")


uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])


if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.success("Excel file uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")


if st.session_state.df is not None:

    df = st.session_state.df.copy()

    st.subheader("🛠 Column Management")

    with st.expander("Edit Columns: Rename, Delete, or Add"):

        st.write("### Rename Column")
        old_col = st.selectbox("Select column to rename", df.columns, key="old_col")
        new_col = st.text_input("Enter new column name", key="new_col")

        if st.button("Rename Column"):
            if new_col.strip():
                df = df.rename(columns={old_col: new_col.strip()})
                st.session_state.df = df
                st.success(f"Column renamed to {new_col}")
                st.rerun()

        st.write("### Delete Column")
        delete_col = st.selectbox("Select column to delete", df.columns, key="delete_col")

        if st.button("Delete Column"):
            df = df.drop(columns=[delete_col])
            st.session_state.df = df
            st.success(f"Column deleted: {delete_col}")
            st.rerun()

        st.write("### Add New Column")
        add_col = st.text_input("Enter new column name", key="add_col")
        default_value = st.text_input("Default value for new column", key="default_value")

        if st.button("Add Column"):
            if add_col.strip():
                df[add_col.strip()] = default_value
                st.session_state.df = df
                st.success(f"Column added: {add_col}")
                st.rerun()

    st.write("### Current Data Preview")
    st.dataframe(df)

    col_options = list(df.columns)

    st.subheader("📌 Confirm Column Mapping")

    name_col = smart_find_column(
        df,
        ["Faculty Name", "Faculty", "Trainer", "Trainee", "Employee Name", "Participant", "Name", "Recipient"],
        "name"
    )

    department_col = smart_find_column(
        df,
        ["Department", "Dept", "Division", "Branch"],
        "department"
    )

    topic_col = smart_find_column(
        df,
        ["Topic", "Training Topic", "Subject", "Session", "Course"],
        "topic"
    )

    date_col = smart_find_column(
        df,
        ["Date", "Training Date", "Session Date"],
        "date"
    )

    time_col = smart_find_column(
        df,
        ["Time", "Training Time", "Timing", "Session Time"],
        "time"
    )

    venue_col = smart_find_column(
        df,
        ["Venue", "Location", "Place", "Class", "Room"],
        "venue"
    )

    email_col = smart_find_column(
        df,
        ["Email", "Email ID", "Mail", "Mail ID", "Email Address"],
        "email"
    )

    name_col = st.selectbox("Name Column", col_options, index=col_options.index(name_col))
    department_col = st.selectbox("Department Column", col_options, index=col_options.index(department_col))
    topic_col = st.selectbox("Topic / Subject Column", col_options, index=col_options.index(topic_col))
    date_col = st.selectbox("Date Column", col_options, index=col_options.index(date_col))
    time_col = st.selectbox("Time Column", col_options, index=col_options.index(time_col))
    venue_col = st.selectbox("Venue / Class Column", col_options, index=col_options.index(venue_col))
    email_col = st.selectbox("Email Column", col_options, index=col_options.index(email_col))

    search_name = st.text_input("🔍 Search Name")

    if search_name:
        df = df[
            df[name_col]
            .astype(str)
            .str.contains(search_name, case=False, na=False)
        ]

    st.info(f"Total Records Found: {len(df)}")

    if st.button("Generate Email Drafts"):
        st.session_state.show_drafts = True

    if st.session_state.show_drafts:

        if st.button("📨 Create Gmail Drafts for All Records"):

            count = 0

            for index, row in df.iterrows():

                name = str(row[name_col])
                department = str(row[department_col])
                topic = str(row[topic_col])
                date = clean_date(row[date_col])
                time = clean_time(row[time_col])
                venue = str(row[venue_col])
                email = str(row[email_col])

                subject = "Training Session Notification"

                html_body = create_html_body(
                    name,
                    department,
                    topic,
                    date,
                    time,
                    venue,
                    recipient_type
                )

                create_draft(email, subject, html_body)
                count += 1

            st.success(f"{count} Gmail drafts created successfully!")

            st.link_button(
                "📬 Open Gmail Drafts",
                "https://mail.google.com/mail/u/0/#drafts"
            )

        for index, row in df.iterrows():

            name = str(row[name_col])
            department = str(row[department_col])
            topic = str(row[topic_col])
            date = clean_date(row[date_col])
            time = clean_time(row[time_col])
            venue = str(row[venue_col])
            email = str(row[email_col])

            subject = "Training Session Notification"

            st.divider()

            st.markdown(
                f"""
                <div style="
                    background-color:#F5F0FA;
                    padding:18px;
                    border-radius:16px;
                    border:1px solid #E0D4F0;
                    margin-top:20px;
                    margin-bottom:15px;
                ">
                    <h3 style="color:#5B2C83;">📄 Draft for {name}</h3>
                    <p><b>To:</b> {email}</p>
                    <p><b>Subject:</b> {subject}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(f"Dear {name},")
            st.write("You are requested to attend the following training session:")

            preview_table = pd.DataFrame({
                recipient_type: [name],
                "Department": [department],
                "Topic": [topic],
                "Date": [date],
                "Time": [time],
                "Venue": [venue]
            })

            st.table(preview_table)

            st.write("Regards,")
            st.write("HR Department")

            html_body = create_html_body(
                name,
                department,
                topic,
                date,
                time,
                venue,
                recipient_type
            )

            if st.button(
                f"📨 Create Gmail Draft for {name}",
                key=f"draft_{index}"
            ):
                create_draft(email, subject, html_body)

                st.success(f"Gmail Draft Created for {name}")

                st.link_button(
                    "📬 Open Gmail Drafts",
                    "https://mail.google.com/mail/u/0/#drafts"
                )

st.divider()
st.caption("Version 1.0")
