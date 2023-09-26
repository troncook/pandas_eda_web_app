from flask import Flask, request, send_file, render_template_string
import pandas as pd
from pandas_profiling import ProfileReport
import os

app = Flask(__name__)

def allowed_file(filename):
    """Check if the uploaded file has a valid extension (either csv or xlsx).
    
    Args:
    filename (str): The name of the uploaded file.
    
    Returns:
    bool: True if the file has a valid extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}

@app.route('/')
def index():
    """Render the main page of the web application with a file upload form.
    
    Returns:
    str: HTML content for the file upload form.
    """
    return render_template_string('''
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br><br>
            <input type="submit" value="Upload and Generate Report">
        </form>
    ''')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and generate a pandas profiling report.
    
    Returns:
    str or flask.Response: A flask Response object to send the generated report file, or an error message as a string.
    """
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if not allowed_file(file.filename):
        return 'File type not allowed. Please upload a CSV or Excel file', 400

    file_path = os.path.join("uploads", file.filename)
    report_directory = 'c:\\Users\\colto\\OneDrive\\Desktop\\startup\\auto_eda\\'
    report_filename = os.path.join(report_directory, "report.html")
    try:
        # Save the file temporarily
        file.save(file_path)
        
        # Read the file into a pandas DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Create a pandas profile report
        profile = ProfileReport(df, explorative=True)
        
        # Save the report as an HTML file
        profile.to_file(report_filename)

        # Add a debug statement to print the file path
        print(f"Report generated at: {report_filename}")
    except Exception as e:
        # Handle various exceptions (e.g., file reading errors, profiling errors)
        if os.path.exists(file_path):
            os.remove(file_path)
        return f"An error occurred: {str(e)}", 500
    finally:
        # Remove the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

    # Add a debug statement to confirm the file exists before sending
    if os.path.exists(report_filename):
        return send_file(report_filename, as_attachment=True)
    else:
        return "Report file not found", 500

if __name__ == '__main__':
    # Ensure the uploads directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Run the Flask application
    app.run(debug=True)