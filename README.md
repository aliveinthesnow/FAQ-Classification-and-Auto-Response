**AI-Powered Email Response Automation**

This project automatically classifies unread Gmail messages using Gemini AI, generates intelligent responses (for FAQ-type queries), sends them via email, updates a Google Sheet, maintains a log in All_Mails.json, labels complex queries, and notifies via Slack. It also updates a running feedback summary in a Google Doc.

**Features**

Gmail integration to fetch unread emails

Gemini-powered classification (Category, Sub-category, Response Type)

Auto-response for FAQs by AI based on context from database

Logs all data to:

All_Mails.json

Google Sheets

Labels complex emails in Gmail & sends Slack alerts for human intervention

Rolling feedback summary update in Google Docs

**Requirements**

A `credentials.json` file which has your Google API access credentials

A `.env` file with:

EMAIL_ADDRESS=your_email

EMAIL_PASSWORD=your_google_generated_app_password(not_the_email_password)

SLACK_WEBHOOK_URL=your_slack_app_webhook_URL

GOOGLE_DOC_ID=ID_in_the_link_to_your_feedback_doc

The following installed packages

`google-auth`

`google-auth-oauthlib`

`google-api-python-client`

`python-dotenv`

`google-generativeai`

Run the script `Main_Code.py`
