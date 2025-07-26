# app.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/get_review_urls", methods=["POST"])
def get_review_urls():
    try:
        data = request.get_json()
        hotel_name = data.get("hotel_name")
        serpapi_key = data.get("serpapi_key")

        print("Input Hotel:", hotel_name)
        print("Using SerpAPI Key:", serpapi_key)

        query = f"{hotel_name} hotel guest reviews and experiences"
        serpapi_url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "num": 20,
            "api_key": serpapi_key,
            "hl": "en",
            "gl": "us"
        }

        response = requests.get(serpapi_url, params=params, timeout=10)
        print("Status Code:", response.status_code)
        print("Response:", response.text)

        if response.status_code != 200:
            return jsonify({"review_urls": [f"Error: SerpAPI returned status {response.status_code}"]})

        results = response.json()
        review_urls = [
            r.get("link") for r in results.get("organic_results", [])[:20]
            if r.get("link") and any(
                kw in r["link"].lower() for kw in ["review", "rating", "guest", "feedback", "experience"]
            )
        ]

        return jsonify({"review_urls": review_urls if review_urls else ["No review-like links found."]})

    except Exception as e:
        return jsonify({"review_urls": [f"Exception occurred: {str(e)}"]})
