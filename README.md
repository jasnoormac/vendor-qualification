Vendor Qualification System - Complete Guide & Project Summary

Overview:
This project is designed to help teams compare and evaluate software vendors intelligently based on specific requirements. Instead of manually reading feature lists, this system uses AI to automatically score how well a vendor matches a set of capabilities like "Budgeting" or "Expense Tracking".

It is built as an API using FastAPI and packaged into a Docker container so it can be run easily without needing to install Python or manage dependencies.

=====================
🛠 Step-by-Step Setup (No Coding Needed)
=====================

1. Install Docker
   - Go to https://www.docker.com/get-started
   - Download and install Docker Desktop for your system (Windows/Mac/Linux)

2. Download the Project
   - Go to the GitHub repository: https://github.com/yourusername/VendorQualification
   - Click "Code" > "Download ZIP" and extract the folder
   OR
   - Use Git (for advanced users): 
     git clone https://github.com/yourusername/VendorQualification.git

3. Open a Terminal (or Command Prompt) and navigate into the project folder:
   cd VendorQualification

4. Build the Docker Image:
   docker build -t vendor-qualification .

5. Run the Application:
   docker run -p 8000:8000 vendor-qualification

6. Use the API:
   - Open your browser and go to http://localhost:8000/docs
   - This will give a brief info about the API that I developed to fetch the targeted vendors
   - Postman or visual studio's Thunder Client extension can be used to hit the API

7.API Details
   - URL: http://localhost:8000/vendor_qualification
   - Header: Content-Type: application/json
   - Body:
        {
         "software_category": "Accounting & Finance",
         "capabilities": ["Budgeting"]
        }
   - Sample Response:
	{
 	 "top_vendors": [
    	    {
      	     "product_name": "Keap",
      	     "average_similarity": 0.5287,
      	     "rating": 4.2,
      	     "category": "CRM Software"
             "product_url": "https://keap.com/pricing",
             "seller": "Keap",
             "full_pricing_page": "https://www.g2.com/products/keap-keap/pricing"
    	    }
  	  ]
	}	  	

=====================
💡 How It Works 
=====================
the system reads from a CSV file of real vendor data. It compares what you need with what each vendor offers using AI-powered text understanding.

Then, it gives you a list of vendors ranked by how well they match your needs — kind of like a personalized recommendation list!

=====================
🧠 Project Approach
=====================

1. Data Processing:
   The input CSV file had a lot of inconsistencies — some feature columns were blank, others were poorly formatted or had special characters. These had to be cleaned using Python's pandas library. The feature descriptions were also embedded in JSON, so they had to be parsed carefully.

   We also removed unnecessary characters (like punctuation), lowercased everything for consistency, and filtered out vendors with no usable features.

2. Similarity Scoring:
   Initially, TF-IDF was used — a classic technique to measure similarity. But it failed to understand the meaning of the capabilities, so we switched to a better method using sentence embeddings from the 'sentence-transformers' library.

   These embeddings allow us to understand the **meaning** of a feature, not just the words. For each vendor, we score how similar their features are to the user’s requested capabilities using these embeddings.

3. Ranking:
   Vendors are ranked using a final score made up of:
   - 70% feature-capability match
   - 30% software category match

   We also factor in the vendor's rating when deciding ties.

=====================
🚧 Challenges Faced
=====================

- Poor Results with TF-IDF: The initial version using traditional similarity failed. It couldn't catch meaning — only exact word matches.
- Messy Data: Many vendors had missing or malformed feature data. We had to write custom parsers and use fallbacks for missing fields like ratings.
- Threshold Tuning: Deciding the cutoff for similarity (like 0.5 or 0.6) was tricky. Too high, and nothing would match. Too low, and irrelevant vendors would be included.
- Server Restarts: During testing, restarting the app would sometimes lock the port ("Address already in use"), which required Docker to be restarted.
- API Testing: Using curl was tedious. Thunder Client in VS Code was much easier and helped speed up debugging.

=====================
🚀 Potential Improvements
=====================

If we had more time, here’s what could make the system even better:

- Let users upload their own vendor CSVs
- Allow users to adjust the similarity threshold on the fly
- Add a front-end using Streamlit or React to make it visually interactive
- Deploy it to the cloud so others can use it without installing Docker
- Use more advanced NLP models (like GPT-style or domain-tuned models)
- Cache embeddings so repeated queries are faster
- Improve error messages and make the API more user-friendly


