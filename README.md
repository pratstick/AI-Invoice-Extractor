AI Invoice Analyzer
===================

**Overview**

AI-Invoice-Analyzer is a web application built with Streamlit that allows users to upload invoices in different formats, such as images or PDFs. The application extracts text from these uploaded files and provides detailed analysis based on the content of the invoices.

Features
--------

-   **Text Extraction:** The application can extract text from image files using Optical Character Recognition (OCR) and from PDF documents.
-   **Invoice Analysis:** It analyzes the extracted text to answer specific questions about the invoice.
-   **User Interface:** The app has a simple and interactive web interface built with Streamlit.

Installation
------------

### Prerequisites

-   Python 3.7 or higher
-   Tesseract OCR engine

### Setup Steps

1.  **Clone the Repository**
    
    Open your terminal or command prompt and run:
    
    `git clone https://github.com/yourusername/AI-Invoice-Analyzer.git
    cd AI-Invoice-Analyzer` 
    
2.  **Create a Virtual Environment**
    
    Run the following command to create a virtual environment:
    
    `python -m venv venv` 
    
3.  **Activate the Virtual Environment**
    
    *   On Windows:
        
        `venv\Scripts\activate` 
        
    *   On macOS or Linux:
        
        `source venv/bin/activate` 
        
4.  **Install Dependencies**
    
    Install the required Python packages by running:
    
    `pip install -r requirements.txt` 
    
    You need to create a `requirements.txt` file with the following contents:
    
    `streamlit
    pillow
    fitz
    pytesseract
    google-generativeai
    python-dotenv` 
    
    To generate this file, you can use:
    
    `pip freeze > requirements.txt` 
    
5.  **Install Tesseract OCR Engine**
    
    *   On Debian/Ubuntu:
        
        `sudo apt-get install tesseract-ocr` 
        
    *   On macOS (using Homebrew):
        
        `brew install tesseract` 
        
    *   On Windows: Download the installer from [Tesseract GitHub Releases](https://github.com/tesseract-ocr/tesseract/releases) and follow the installation instructions. Make sure to add the Tesseract executable to your system’s PATH.
6.  **Set Up Environment Variables**
    
    Create a file named `.env` in the root directory of your project and add your Google API key with the following content:
    
    `GOOGLE_API_KEY=your_google_api_key_here` 
    

### Running the Application

1.  **Start the Streamlit App**
    
    In your terminal or command prompt, run:
    
    `streamlit run app.py` 
    
2.  **Open the Application**
    
    Open your web browser and go to `http://localhost:8501` to use the application.
    

Deployment
----------

###Deploying on Streamlit Community Cloud

1.  **Create a New App**
    
    Go to Streamlit Community Cloud and log in with your GitHub account. Click "New app" and link your repository.
    
2.  **Configure the Deployment**
    
    Set up the deployment by specifying the `app.py` file. Ensure that the `.env` file is included in your repository or configure environment variables directly on Streamlit Community Cloud.
    
3.  **Deploy**
    
    Click "Deploy" to start the deployment process. Streamlit Community Cloud will automatically install dependencies and deploy your app.
    

### Deploying on Other Platforms

For other cloud platforms like Heroku or AWS, follow their respective documentation for deploying Python web applications. You may need to adjust the configuration for environment variables and dependency management.

**Usage**

1.  **Upload Invoice:** Choose an image (JPEG, PNG) or PDF of the invoice.
    
2.  **Provide Input Prompt:** Enter the text prompt asking questions about the invoice.
    
3.  **Analyze:** Click the "Tell me about my invoice" button to get detailed responses based on the extracted text.
    

Contributing
------------

Feel free to fork the repository and submit pull requests. Make sure any contributions are well-documented and tested.

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for details.

**Contact**

For questions or support, please open an issue on the [GitHub repository](https://github.com/pratstick/AI-Invoice-Extractor).