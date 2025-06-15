print("Attempting to import Document from langchain.schema.document...")
try:
    from langchain.schema.document import Document
    print("Import successful!")
    print(f"Document type: {type(Document)}")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
print("Test script finished.")
