from __future__ import print_function
import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


"""Authentication for google docs and google drive"""
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

class GoogleDocsTool:

    def __init__(self):
        creds = None
        """Checks if token exists."""
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(os.path.join(os.path.dirname(__file__), '..', 'credentials.json'),SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.creds = creds
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        about = self.drive_service.about().get(fields="user(emailAddress)").execute()
        print(f"Authenticated as: {about['user']['emailAddress']}")


    def create_document(self, title: str) -> str:
        """Creates a document with the corresponding title."""
        """Title is the title of the document"""
        
        body = {'title': title}
        doc = self.docs_service.documents().create(body=body).execute()
        print(f"Document Created: {doc.get('title')} (ID: {doc.get('documentId')})")
        return doc.get('documentId')
    
    def get_document_id_by_title(self, title: str) -> str:
        """Gets the file id of the exact or similar title."""

        query = (f"mimeType='application/vnd.google-apps.document' and "
            f"name contains '{title}'")

        result = self.drive_service.files().list(
        q=query,spaces='drive',fields='files(id, name)',pageSize=100).execute()

        files = result.get('files', [])

        for file in files:
            print(f"Found File: {file['name']} (ID: {file['id']})")
            
            if file['name'].strip().lower() == title.strip().lower():
                return file['id']

        return None
            
    def write_to_document(self, document_id: str, text: str):
        """Writes to the created or existing google document."""
        
        request = [{'insertText': {'location': {'index': 1,},'text': text}}]
        result = self.docs_service.documents().batchUpdate(documentId=document_id, body={'requests': request}).execute()
        print(f"Written to Document: {document_id}: {result}")

    def read_document(self, doc_id):
        """Reads and returns text from the specified google doc"""
        
        try:
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = doc.get("body", {}).get("content", [])

            full_text = ""
            for element in content:
                paragraph = element.get("paragraph")
                if not paragraph:
                    continue
                for line in paragraph.get("elements", []): 
                    text_run = line.get("textRun")
                    if text_run:
                        full_text += text_run.get("content", "")
            
            return full_text.strip()
        except Exception as e:
            print(f"Error reading document: {e}")
            return None
    
    def append_to_document(self, document_id: str, text: str):
        """Appends text to the end of the Google Document."""

        doc = self.docs_service.documents().get(documentId=document_id).execute()
        end_index = doc.get('body').get('content')[-1].get('endIndex', 1)

        request = [{"insertText": {"location": {"index": end_index - 1},"text": text}}]
        result = self.docs_service.documents().batchUpdate(
            documentId=document_id,body={'requests': request}).execute()

        print(f"Appended text to Document: {document_id}: {text}")
        return result
    
    def clear_document(self, document_id: str):
        """Deletes all content from the document."""

        doc = self.docs_service.documents().get(documentId=document_id).execute()
        end_index = doc.get('body').get('content')[-1].get('endIndex', 1)

        if end_index <= 1:
            return "Document is already empty."

        requests = [{'deleteContentRange': {'range': {'startIndex': 1,'endIndex': end_index - 1}}}]

        result = self.docs_service.documents().batchUpdate(
            documentId=document_id,body={'requests': requests}).execute()

        return f"Cleared document: {document_id}"
                
    def delete_document(self, document_id: str) -> str:
        """Deletes a Google Doc."""

        try:
            self.drive_service.files().delete(fileId=document_id).execute()
            return "Document deleted successfully."
        
        except Exception as e:
            return f"Error deleting document: {str(e)}"