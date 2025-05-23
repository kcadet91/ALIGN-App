import streamlit as st
import re
import pandas as pd
from collections import Counter
import requests

# --- Setup Hugging Face API for DeepSeek ---
HUGGINGFACE_API_TOKEN = st.secrets["HUGGINGFACE_API_TOKEN"]

# --- Expanded Sensitive Keyword List ---
sensitive_keywords = {
    word: 1 for word in set([
        "activism", "activists", "advocacy", "advocate", "advocates",
        "barrier", "barriers", "biased", "biased toward", "biases", "biases towards",
        "bipoc", "black and latinx", "community diversity", "community equity",
        "cultural differences", "cultural heritage", "culturally responsive",
        "disabilities", "disability", "discriminated", "discrimination", "discriminatory",
        "diverse backgrounds", "diverse communities", "diverse community", "diverse group",
        "diverse groups", "diversified", "diversify", "diversifying", "diversity and inclusion",
        "diversity equity", "enhance the diversity", "enhancing diversity", "equal opportunity",
        "equality", "equitable", "equity", "ethnicity", "excluded", "female", "females",
        "fostering inclusivity", "gender", "gender diversity", "genders", "hate speech",
        "hispanic minority", "historically", "implicit bias", "implicit biases", "inclusion",
        "inclusive", "inclusiveness", "inclusivity", "increase diversity", "increase the diversity",
        "indigenous community", "inequalities", "inequality", "inequitable", "inequities",
        "institutional", "lgbt", "marginalize", "marginalized", "minorities", "minority",
        "multicultural", "polarization", "political", "prejudice", "privileges", "promoting diversity",
        "race and ethnicity", "racial", "racial diversity", "racial inequality", "racial justice",
        "racially", "racism", "sense of belonging", "sexual preferences", "social justice",
        "sociocultural", "socioeconomic", "status", "stereotypes", "systemic", "trauma",
        "under appreciated", "under represented", "under served", "underrepresentation",
        "underrepresented", "underserved", "undervalued", "victim", "women", "women and underrepresented"
    ])
}

# --- Functions ---
def simple_tokenize(text):
    return re.findall(r'\b\w[\w-]*\b', text.lower())

def flag_sensitive_terms(text):
    tokens = simple_tokenize(text)
    token_counts = Counter(tokens)
    flagged = {kw: token_counts[kw] for kw in sensitive_keywords if kw in token_counts}
    return flagged

def compute_risk_score(flagged_terms):
    return sum(sensitive_keywords[word] * count for word, count in flagged_terms.items())

def estimate_percentile(score):
    if score == 0: return 1
    elif score < 5: return 25
    elif score < 10: return 50
    elif score < 20: return 75
    else: return 90

def risk_level_tag(percentile):
    if percentile <= 25:
        return "🟢 Low"
    elif percentile <= 50:
        return "🟡 Moderate"
    elif percentile <= 75:
        return "🟠 High"
    else:
        return "🔴 Very High"

def review_pathway(title, summary, description):
    for section, text in [("Title/Abstract", title), ("Project Summary", summary)]:
        if flag_sensitive_terms(text):
            return f"Category 3: DEIA/EO language flagged in {section}."
    if flag_sensitive_terms(description):
        return "Category 3: DEIA/EO language flagged in Project Description."
    return "Category 1: No DEIA/EO language found. Add justification comment."

def highlight_text(text, flagged_terms):
    for term in flagged_terms:
        pattern = re.compile(rf"(?i)\b({re.escape(term)})\b")
        text = pattern.sub(r'<span style="background-color: yellow;">\1</span>', text)
    return text

def suggest_alternatives(text, flagged_terms):
    prompt = f"""Rewrite this grant narrative to reduce political risk by rewording or replacing the following terms, while preserving the original meaning and intent.

Flagged terms: {', '.join(flagged_terms)}

Original text:
{text}
"""
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result[0]["generated_text"] if isinstance(result, list) else result["generated_text"]
        else:
            return f"[API Error {response.status_code}] {response.text}"
    except Exception as e:
        return f"[Exception occurred] {str(e)}"


# --- Streamlit App UI ---
st.set_page_config(page_title="ALIGN", layout="wide")

# --- Custom Style ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica Neue', sans-serif;
            background-color: #f7f9fc;
        }
        h1 {
            color: #183D5D;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stButton > button {
            background-color: #183D5D;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div style="background-color:#1B355D; padding: 2rem 1rem; border-radius: 8px;">
        <h1 style='color: white; font-size: 38px; font-family: "Segoe UI", "Open Sans", sans-serif; text-align: center;'>
            ALIGN: Assessing Language Impact for Grant Narratives
        </h1>
    </div>
    <div style='padding-top: 1rem;'>
        <p style='font-size: 17px; font-family: "Segoe UI", "Open Sans", sans-serif; color: #333; text-align: center;'>
            This tool is a prototype to support transparency and awareness in grant language and
        it does not reflect official agency guidance or guarantee any funding outcome.
            Always consult your program officer or institutional grant support office.
        </p>
    </div>
""", unsafe_allow_html=True)


agency = st.selectbox("Select Funding Agency Profile", ["NIH", "NSF", "Other"])

# --- Inputs ---
col1, col2 = st.columns(2)
with col1:
    title_text = st.text_area("Paste your Title or Abstract", height=100)
with col2:
    summary_text = st.text_area("Paste your Project Summary", height=100)
description_text = st.text_area("Paste your Project Description", height=200)

# --- Button Logic ---
if st.button("Analyze"):
    combined_text = " ".join([title_text, summary_text, description_text])
    if combined_text.strip():
        flagged = flag_sensitive_terms(combined_text)
        score = compute_risk_score(flagged)
        percentile = estimate_percentile(score)

        st.markdown("<h3 style='color:#1c1c1c;'>Risk Analysis</h3>", unsafe_allow_html=True)
        st.write(f"**Risk Score:** {score}")
        st.markdown("**Risk Score Definition:** Total frequency of flagged terms. Higher scores suggest greater likelihood of scrutiny.")
        st.write(f"**Estimated Risk Percentile:** {percentile}th percentile")
        st.write(f"**Risk Level:** {risk_level_tag(percentile)}")

        if flagged:
            st.markdown("<h3 style='color:#1c1c1c;'>Flagged Terms</h3>", unsafe_allow_html=True)
            df = pd.DataFrame(flagged.items(), columns=["Term", "Frequency"])
            st.dataframe(df)

            st.markdown("<h3 style='color:#1c1c1c;'>Highlighted Text</h3>", unsafe_allow_html=True)
            highlighted = highlight_text(combined_text, flagged)
            st.markdown(highlighted, unsafe_allow_html=True)

            st.markdown("<h3 style='color:#1c1c1c;'>Suggested Rewording</h3>", unsafe_allow_html=True)
            suggestions = suggest_alternatives(combined_text, flagged)
            st.write(suggestions)
        else:
            st.success("No sensitive terms flagged. Low risk detected.")

        st.markdown("<h3 style='color:#1c1c1c;'>Flowchart Review Classification</h3>", unsafe_allow_html=True)
        st.write(review_pathway(title_text, summary_text, description_text))
    else:
        st.warning("Please paste content into one or more fields to analyze.")

# --- Footer ---
st.markdown("""
    <hr>
    <p style="font-size: 14px; color: #555;">
    <strong>Maintainer:</strong> Dr. Kechna Cadet – Substance Use Epidemiologist<br>
    For feedback or collaboration, please contact Dr. Cadet at kc3010@cumc.columbia.edu.
    </p>
""", unsafe_allow_html=True)
