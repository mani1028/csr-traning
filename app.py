from flask import Flask, render_template, request, jsonify
from docx import Document
import os
import re

app = Flask(__name__)

DATA_FOLDER = "data"

INDUSTRY_FILES = {
    "E-COMMERCE": "E-COMMERCE – CSR 1.docx",
    "VEHICLE": "VEHICLE SERVICE CENTER – CSR 1.docx",
    "TELECOM": "TELECOM  INTERNET  SATELLITE TV CSR Q&A 1.docx",
    "IT": "IT HARDWARE – CSR 1.docx",
    "HOTEL": "HOTEL & RESTAURANT – CSR 1.docx",
    "HEALTHCARE": "HEALTHCARE DOCTOR APPOINTMENT – CSR Q&A 1.docx",
    "CAR_RENTAL": "car rentals Q&A CSR 1.docx"
}

def load_scenarios(docx_file):
    path = os.path.join(DATA_FOLDER, docx_file)
    # Error handling in case file doesn't exist
    if not os.path.exists(path):
        return []

    doc = Document(path)

    scenarios = []
    current_scenario_type = "GENERAL"
    customer = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect scenario headings
        if "GOOD" in text.upper() and "SCENARIO" in text.upper():
            current_scenario_type = "🟢 GOOD / NORMAL CUSTOMER"
            continue

        if "ANGRY" in text.upper() or "DIFFICULT" in text.upper():
            current_scenario_type = "🔴 ANGRY / DIFFICULT CUSTOMER"
            continue

        if "ESCALATION" in text.upper() or "THREAT" in text.upper():
            current_scenario_type = "🔥 ESCALATION / THREATENING"
            continue

        # --- FIX STARTS HERE ---
        # Detect 'Customer:' OR 'Patient:' (Case insensitive)
        if re.search(r'(customer|patient)\s*:', text, re.IGNORECASE):
            # Split using non-capturing group (?:...) to ensure we just get the text part
            customer = re.split(r'(?:customer|patient)\s*:', text, flags=re.IGNORECASE)[-1].strip()

        # Detect CSR answer
        elif re.search(r'csr\s*:', text, re.IGNORECASE) and customer:
            csr = re.split(r'csr\s*:', text, flags=re.IGNORECASE)[-1].strip()
            scenarios.append({
                "scenario_type": current_scenario_type,
                "customer": customer,
                "ideal": csr
            })
            customer = None
        # --- FIX ENDS HERE ---

    return scenarios

@app.route("/")
def index():
    return render_template("index.html", industries=INDUSTRY_FILES.keys())

@app.route("/start", methods=["POST"])
def start():
    industry = request.json["industry"]
    # Check if key exists to prevent crash
    if industry not in INDUSTRY_FILES:
         return jsonify({"error": "Industry not found"})
         
    scenarios = load_scenarios(INDUSTRY_FILES[industry])

    if not scenarios:
        return jsonify({"error": "No scenarios found! Check if file uses 'Customer:' or 'Patient:' labels."})

    return jsonify(scenarios)

if __name__ == "__main__":
    app.run(debug=True)