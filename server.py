from flask import Flask, request, redirect
import time, os
from pathlib import Path
from process import process_resume
# from pymongo import MongoClient


app = Flask(__name__)

# client = MongoClient('mongodb://localhost:27017/')  
# db = client['your_database_name']
# collection = db['pdf_collection']

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    print(f"Received POST request to /upload-pdf with data: {request.data}")
    # Check if a file was included in the POST request
    print(dict(request.files))
    if 'pdf_file' not in request.files.keys():
        return "No PDF file provided in the request", 400

    pdf_file = request.files['pdf_file']



    # Check if the file has an allowed extension (e.g., .pdf)
    allowed_extensions = {'pdf'}
    if pdf_file and pdf_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        # You can now process or save the PDF file as needed
        # For example, you can save it to a specific folder

        pdf_file.save('uploads/' + str(time.time())+pdf_file.filename)
        # pdf_data = pdf_file.read()
        # db_entry = {"filename": pdf_file.filename, "pdf_data": pdf_data}
        # collection.insert_one(db_entry)

        return redirect(("http://127.0.0.1:3000/"))
    else:
        return "Invalid file format. Only PDF files are allowed", 400
@app.route('/getParsedResume', methods=['GET'])
def getParsedResume():
    file_name = request.args.get("file_name")
    with open(f"uploads/{file_name}", 'rb') as file:
        data = file.read()
    parsed_data = process_resume(data)
    return f"{parsed_data['sections']['projects']},{parsed_data['sections']['experience']}"
@app.route('/getAnalytics', methods=['GET'])
def getAnalytics():
    pdfs = os.listdir("uploads")
    data = []
    for pdf in pdfs:
        with open(f"uploads/{pdf}", 'rb') as file:
            data.append(process_resume(file.read()))
    return data

if __name__ == '__main__':
    folder = Path.cwd() / "uploads"
    folder.mkdir(exist_ok=True)
    app.run(debug=True)