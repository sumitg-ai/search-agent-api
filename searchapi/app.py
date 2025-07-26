# searchapi/app.py

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/get_review_urls", methods=["POST"])
def get_review_urls():
    try:
        data = request.get_json()
        hotel_name = data.get("hotel_name")
        serpapi_key = os.environ.get("SERPAPI_KEY")  # Loaded from Render env var

        if not hotel_name:
            return jsonify({"review_urls": ["Missing 'hotel_name' in request body."]}), 400

        if not serpapi_key:
            return jsonify({"review_urls": ["Missing 'SERPAPI_KEY' in environment variables."]}), 500

        print("🔍 Searching reviews for:", hotel_name)
        print("🔑 SerpAPI Key (masked):", serpapi_key[:6] + "****")

        # Build query
        query = f"{hotel_name} hotel guest reviews and experiences"
        params = {
            "engine": "google",
            "q": query,
            "num": 20,
            "api_key": serpapi_key,
            "hl": "en",
            "gl": "us"
        }

        print("📡 Sending request to SerpAPI...")
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)

        print("🧾 Status Code:", response.status_code)
        if response.status_code != 200:
            return jsonify({"review_urls": [f"SerpAPI error {response.status_code}"]}), 502

        results = response.json()
        review_urls = [
            r.get("link") for r in results.get("organic_results", [])[:20]
            if r.get("link") and any(
                kw in r["link"].lower() for kw in ["review", "rating", "guest", "feedback", "experience"]
            )
        ]

        print("✅ Extracted URLs:", review_urls)
        return jsonify({
            "review_urls": review_urls if review_urls else ["No review-like links found."]
        })

    except Exception as e:
        print("❌ Exception:", str(e))
        return jsonify({"review_urls": [f"Exception occurred: {str(e)}"]}), 500
        

# Entry point for Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)