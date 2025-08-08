from mcp.server.fastmcp import FastMCP
from tools.google_doc_tools import GoogleDocsTool
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

mcp = FastMCP('Siddhartha')
tool = GoogleDocsTool()

def search_document(title: str) -> str:
    """Searches for documents with the same title or a similar title."""

    doc_id = tool.get_document_id_by_title(title)
    if not doc_id:
        print(f"Error! Document with title {title} not found!")
        return None
    return doc_id

def clear_document(title: str)->str:
    """Clears all data in the document."""

    doc_id = search_document(title)
    tool.clear_document(doc_id)
    

@mcp.tool()
def search_doc(title: str) -> str:
    """Searches for documents with the same title or a similar title."""

    doc_id = tool.get_document_id_by_title(title)
    if not doc_id:
        return f"Document with title '{title}' not found."
    return doc_id

@mcp.tool()
def create_google_doc(title: str) -> str:
    """Creates a google document with the given title if it does not exist"""

    doc_id = tool.get_document_id_by_title(title)
    if not doc_id:
        doc_id = tool.create_document(title)
    
    else:
        return f"Document with title '{title}' already exists."
    
    return doc_id

@mcp.tool()
def write_to_google_doc(title: str, content: str) -> str:
    """Writes to a Google Doc. Creates it only if not already existing."""
    
    doc_id = tool.get_document_id_by_title(title)

    if not doc_id:
        doc_id = tool.create_document(title)

    result = tool.write_to_document(doc_id, content)
    return result

@mcp.tool()
def read_from_google_doc(title: str) -> str:
    """Reads from an existing Google Doc and returns the content."""
    
    doc_id = search_document(title)
    content = tool.read_document(doc_id)
    
    if content is None:
        return f"Failed to read content from document '{title}'."
    if not content.strip():
        return f"Document '{title}' appears to be empty."
    
    return content

@mcp.tool()
def append_to_doc(title: str,content:str) -> str:
    """Appends text to the end of the document."""

    doc_id = search_document(title)
    result = tool.append_to_document(doc_id,content)
    return result
    
@mcp.tool()
def clear_doc(title: str)->str:
    """Deletes/Clears all data in the document."""

    doc_id = search_document(title)
    result = tool.clear_document(doc_id)
    return result

@mcp.tool()
def delete_doc(title: str) -> str:
    """Deletes the entire document."""

    doc_id = tool.get_document_id_by_title(title)
    if not doc_id:
        return f"Error, document with title {title} does not exist!"
    result = tool.delete_document(doc_id)
    return result
    
def main():
    mcp.run()

if __name__ == "__main__":
    main()
    

