from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import json
import re
from sentence_transformers import SentenceTransformer, util
import uvicorn

# Initialize FastAPI and model
app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the dataset
df = pd.read_csv("./CRM_Category_Product_Overviews.csv")

# --------- PREPROCESSING SECTION ---------

# Drop completely empty columns
df.dropna(axis=1, how="all", inplace=True)

# Fill common NaN fields with safe defaults
fill_defaults = {
    "rating": 0,
    "main_category": "Unknown Category",
    "product_name": "Unnamed Software",
    "Features": "[]",  # avoid JSON decode errors
}
df.fillna(value=fill_defaults, inplace=True)

# Strip whitespace from string fields
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].astype(str).str.strip()

# Clean feature text lightly (no stopwords)
def clean_text(text):
    text = text.lower()
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)  
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)  
    return text.strip()

# Parse and clean feature descriptions
def parse_features(features_str):
    try:
        features_json = json.loads(features_str)
        descriptions = []
        for category in features_json:
            for feature in category.get("features", []):
                desc = feature.get("description", "").strip()
                if desc:
                    descriptions.append(clean_text(desc))
        return descriptions
    except:
        return []

# Parse and filter
df["Parsed_Features"] = df["Features"].apply(parse_features)
df_clean = df[df["Parsed_Features"].map(len) > 0].copy()
df_clean = df_clean[df_clean["main_category"].notnull()].copy()

# Precompute embeddings
df_clean["Feature_Embeddings"] = df_clean["Parsed_Features"].apply(
    lambda feats: [model.encode(f, convert_to_tensor=True) for f in feats]
)

# Request schema
class VendorRequest(BaseModel):
    software_category: str
    capabilities: List[str]

@app.post("/vendor_qualification")
def vendor_qualification(request: VendorRequest):
    if not request.capabilities:
        raise HTTPException(status_code=400, detail="Capabilities list is empty.")

    # Enrich each capability with category context
    enriched_queries = [
        f"{cap} in {request.software_category}" for cap in request.capabilities
    ]
    enriched_query_embeddings = [
        model.encode(q, convert_to_tensor=True) for q in enriched_queries
    ]

    # Also embed software category as its own dimension
    software_category_embedding = model.encode(request.software_category, convert_to_tensor=True)

    results = []

    for _, row in df_clean.iterrows():
        feature_embs = row.Feature_Embeddings

        # Score capability matches
        capability_scores = []
        for query_emb in enriched_query_embeddings:
            max_sim = max([util.cos_sim(query_emb, feat_emb).item() for feat_emb in feature_embs])
            capability_scores.append(max_sim)

        # Score category match
        category_score = max([util.cos_sim(software_category_embedding, feat_emb).item() for feat_emb in feature_embs])

        # Final score: 70% from capabilities, 30% from category context
        combined_score = float(np.mean(capability_scores) * 0.7 + category_score * 0.3)

        if combined_score >= 0.5:
            results.append({
                "product_name": row.product_name,
                "average_similarity": round(combined_score, 4),
                "rating": row.rating,
                "category": row.main_category,
                "product_url": row.product_url,
                "seller": row.seller,
                "full_pricing_page": row.full_pricing_page,
            })

    if not results:
        return {"message": "No vendors found with semantic relevance to the query."}

    results = sorted(results, key=lambda x: (x["average_similarity"], x["rating"] or 0), reverse=True)
    return {"top_vendors": results[:10]}

# Run with: uvicorn vendor_qualification_api:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
