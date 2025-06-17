import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import json
from datetime import datetime    #so I can insert into sheet
import google.generativeai as genai
import sqlite3
from email.mime.text import MIMEText
import base64    #used to get the received mail in the plain text
from googleapiclient.discovery import build
import smtplib
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

def ai_category(subject, content):
    prompt = f"""I am giving you the subject and content from a mail my company has received.
    You must respond with a single word, which will be the classification of the email. Classify it as either 'Query' or 'Feedback', with case-sensitivity exactly as I gave in the quotes. If an email is not a query, give the output as 'Feedback' by default. Answer as only 1 word, nothing else
    Subject - {subject}
    Content - {content}
"""
    response = model.generate_content(prompt)
    return response.text

def ai_subcategory(subject, content):
    prompt = f"""I am giving you the subject and content from a mail my company has received. You must respond with a single word, which will be the classification of the email.
    Classify it as one of the following -
    'Returns', 'Retail', 'Website', 'App', 'Orders', 'Shipping' and 'Payments'
    based on what the query is like
    Here is the subject and content
    Subject - {subject}
    Content - {content}
"""
    response = model.generate_content(prompt)
    return response.text

def fetch_faqs_by_category(sub_category):
    db_path = 'faq_database.db'  # Make sure this path is correct
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT question, answer FROM faqs WHERE category = ?"
    cursor.execute(query, (sub_category,))
    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return "No FAQ data available for this category."

    # Format the rows into a readable string for Gemini
    faqs_text = ""
    for question, answer in rows:
        faqs_text += f"Q: {question}\nA: {answer}\n\n"

    return faqs_text.strip()

def ai_responsetype(subject, content, data_of_sub_category):
    prompt = f"""I am giving you the subject and content from a mail my company has received.
        You must respond with a single word, which will be the classification of the email.
        Classify it as either 'FAQ' if it is directly a question from, or is one related to the database I give you, else classify it as 'Complex'
        Here is the subject and content
        Subject - {subject}
        Content - {content}
        Here is the database - {data_of_sub_category}
    """
    response = model.generate_content(prompt)
    return response.text

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/documents']

def ai_automated_response(subject, content, data_of_sub_category, example_data):
    prompt = f"""I am giving you all the usual FAQs for the category of the email FAQ our company has received. You need to generate a personalized reply email (ONLY CONTENT, NOT SUBJECT) based on context from the database I give you and the questions that the person has asked. The FAQ database only has a very succinct answer, which you are supposed to elongate slightly and make more professional sounding, personalized for the customer
    You need to be polite, slightly succinct and confident in your tone.
    Here is some information about the company -
    
    [Company Name: UrbanThread Co.
    Tagline: Style Meets Simplicity.
    
    About Us:
    UrbanThread Co. is a digitally native apparel brand redefining everyday fashion with bold ideas and seamless customer experiences. Founded in 2022, our mission is to make high-quality, minimalist fashion accessible to modern consumers who value both comfort and expression.
    We design, manufacture, and deliver wardrobe essentials with a focus on clean aesthetics, ethical sourcing, and tech-enabled service. From stylish basics to statement prints, every piece is made to fit your lifestyle — not the other way around.
    
    What Makes Us Different:
    Sustainably Sourced: We use 100% organic cotton and recycled fabrics for over 85% of our product line.
    Design Philosophy: Minimal. Versatile. Timeless. We believe fashion should be effortless.
    Fast Fulfillment: All orders ship within 48 hours, with real-time tracking and smooth returns.
    
    Our Customers:
    Over 20,000 happy customers across India, with strong communities in Bengaluru, Mumbai, and Delhi. We serve students, creators, professionals — anyone who values originality and ease.]
 
    Here is an example:
    Here is the database - {example_data}
    Subject of received email - Problem with my order
    Content of received email - Hi, I had ordered a pair of sunglasses on your website. Unfortunately I had ordered the wrong ones by mistake. I actually need a different color. Can I cancel the order? Or can I at least modify my order so I get my desired color?
    Kindly look into this
    Thanks
    
    What you will generate - Dear Customer,
    We understand that your order was incorrectly placed. This is a very common issue and there is no need to worry. We are very flexible with our customer's orders and value them. However, modifications post ordering are not possible.\nHowever, you may either cancel the order, or, if it has been shipped, book a return and then reorder with your desired color.\nTo cancel an order, simply head over to the 'My Orders' section and click 'Cancel' next to the sunglasses you ordered
    If you require any further assistance, feel free to reach out to us anytime.
    
    Sincerely,
    
    Rakesh,
    Customer Relationship Manager,
    The UrbanThread Co.
    
    Here is the database - {data_of_sub_category}
    Subject of received email - {subject}
    Content of received email - {content}
    
    Your reply should be only the content, nothing else.
    """

    response = model.generate_content(prompt)
    return response.text

def ai_feedback_rolling_summary(prev_summary, subject, content):
    prompt = f"""You are supposed to generate a rolling summary for all emails I receive in my emails, which I'll enter into my Google Docs. I will be sharing with you the previous summary that I have, and the subject and content of the new mail I have received.
    Your goal is to make a new summary, that should cover all points from the previous summary and the new input combined. It might very well happen that the new content does not really have any feedback, but are just questions. You have to reason and figure out whether the new mail has some substantial data or feedback that can be used by the company.
    If it does, you can very well ignore the new mail entirely. However, the final summary must have all of the required points, feedback and feature requests
    Your response will be of the following format:
    Summary -
    1. Positive -
    Something..........
    
    2. Negative - 
    Things they don't like.....
    
    
    Feature Requests -
    1. something.......
    2. something.....
    
    Issues and Problems -
    Something.....
    
    If the new mail has something new, or something that sort of matches the previous summary, you may merge points and feedbacks to make a finalized version. Do not make up any part of the feedback, only include what has actually been said. Do not hallucinate, and do not remove any older feedback.
    Here is the data
    Previous Summary - {prev_summary}
    New Mail Subject - {subject}
    New Mail Content - {content}
    
    your response must contain only the summary and nothing else, only in the format I have requested.
    """

    response = model.generate_content(prompt)
    return response.text

def authentication():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    gmail_creds = build('gmail', 'v1', credentials=creds)
    sheet_creds = build('sheets', 'v4', credentials=creds)
    docs_creds = build('docs', 'v1', credentials=creds)
    return gmail_creds, sheet_creds, docs_creds

def get_current_feedback_summary(docs_creds, document_id):
    doc = docs_creds.documents().get(documentId=document_id).execute()
    text = ""
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for item in element['paragraph'].get('elements', []):
                text_run = item.get('textRun')
                if text_run and 'content' in text_run:
                    text += text_run['content']
    return text.strip()

def update_feedback_summary_doc(docs_creds, document_id, new_summary):
    # First, fetch the document to get the full length
    doc = docs_creds.documents().get(documentId=document_id).execute()
    end_index = doc.get('body', {}).get('content', [])[-1].get('endIndex', 1)

    requests = [
        {
            "deleteContentRange": {
                "range": {
                    "startIndex": 1,
                    "endIndex": end_index - 1  # leave index 0 intact (can't delete that)
                }
            }
        },
        {
            "insertText": {
                "location": {
                    "index": 1
                },
                "text": new_summary
            }
        }
    ]

    docs_creds.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests}
    ).execute()

def send_slack_message(message_text):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    payload = {
        "text": message_text
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, json=payload, headers=headers)

def main_function(gmail_creds, sheet_creds, docs_creds):
    response = gmail_creds.users().messages().list(
        userId='me',
        labelIds=['INBOX', 'UNREAD'],
        maxResults=10
    ).execute()

    messages = response.get('messages', [])

    if not messages:
        print("You don't have any unread emails rn")
    else:
        print(f"Found {len(messages)} unread emails")

    doc_id = os.getenv("GOOGLE_DOC_ID")
    prev_summary = get_current_feedback_summary(docs_creds, doc_id)

    for hey in messages:
        hey_id = hey['id']
        each_mail_received = gmail_creds.users().messages().get(userId='me', id=hey_id).execute()

        subject = None
        content = None
        sent_from = None
        for some_header in each_mail_received['payload']['headers']:
            if some_header['name'] == 'Subject':
                subject = some_header['value']
            if some_header['name'] == 'From':
                sent_from = some_header['value']
        for part in each_mail_received['payload'].get('parts', []):
            if part['mimeType'] == 'text/plain':
                body_data = part['body']['data']
                content = base64.urlsafe_b64decode(body_data).decode()

            # other cases, when there is directly just the body
        body_data = each_mail_received['payload']['body'].get('data')
        if body_data:
            content = base64.urlsafe_b64decode(body_data).decode()

        category = ai_category(subject, content).strip()
        sub_category = ""  #retail, etc.
        response_type = ""  #FAQ or complex

        if (category.lower() == "query"):
            sub_category = ai_subcategory(subject, content).strip()
        else:
            sub_category = "NIL"

        data_of_sub_category = fetch_faqs_by_category(sub_category)  # the data for a particular sub_category
        example_data = fetch_faqs_by_category("Orders")

        if (category.lower() == "query"):
            response_type = ai_responsetype(subject, content, data_of_sub_category).strip()
        else:
            response_type = "NIL"
        status = "Pending"
        mail_sent = "NIL"

        #sending the email here
        if (response_type == "FAQ"):
            ai_gen_resp = ai_automated_response(subject, content, data_of_sub_category, example_data)
            message = MIMEText(ai_gen_resp)
            sending_mail_id = os.getenv("EMAIL_ADDRESS")
            password = os.getenv("EMAIL_PASSWORD")
            message['From'] = sending_mail_id
            message['To'] = sent_from
            message['Subject'] = "Reply to raised query"
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(sending_mail_id, password)
                smtp.send_message(message)
            #raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            #message_body = {
            #    'raw': raw_message
            #}
            #gmail_creds.users().messages().send(userId='me', body=message_body).execute()
            status = "Email Sent"
            mail_sent = ai_gen_resp

        email_data = {
            "from": sent_from,
            "subject": subject,
            "content": content,
            "category": category,
            "sub_category": sub_category,
            "response_type": response_type,
            "status": status,
            "mail_sent": mail_sent
        }

        with open('All_Mails.json', 'r') as file:
            data = json.load(file)
        data.append(email_data)
        with open('All_Mails.json', 'w') as file:
            json.dump(data, file, indent=4)

        timestamp = datetime.now().isoformat()
        sheet_row = [sent_from, subject, content, category, sub_category, response_type, timestamp, status, mail_sent]
        add_to_sheet(sheet_creds, sheet_row)

        if (response_type == "Complex"):
            label_id = None
            results = gmail_creds.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            for label in labels:
                if label['name'].strip().lower() == "Complex_Queries".lower():
                    label_id=label['id']
                    break

            gmail_creds.users().messages().modify(
                userId='me',
                id=hey_id,
                body={
                    'addLabelIds': [label_id]   #this will add a label to that
                }
            ).execute()

            slack_message = f"Respond to a complex mail from {sent_from}"
            send_slack_message(slack_message)

        #doing the feedback part now....
        prev_summary = ai_feedback_rolling_summary(prev_summary, subject, content)

    update_feedback_summary_doc(docs_creds, doc_id, prev_summary)

Sheet_ID = '1va5hfXBBf8sqFFeGuLzpBpSm-uFPbQlc7w_0j5zXyXg'
Sheet_Name = 'Sheet1'

def add_to_sheet(sheet_creds, data):
    range_ = f"{Sheet_Name}!A:I" # A to I are what I need
    body = {
        'values': [data]
    }

    sheet_creds.spreadsheets().values().append(
        spreadsheetId=Sheet_ID,
        range=range_,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

if __name__ == '__main__':
    gmail_creds, sheet_creds, docs_creds = authentication()
    main_function(gmail_creds, sheet_creds, docs_creds)
    print("Successfully Executed")