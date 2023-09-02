from flask import Flask, request, redirect
import time
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

if __name__ == '__main__':
    app.run(debug=True)