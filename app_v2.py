import streamlit as st
import re
import pandas as pd
from collections import Counter
import requests

# --- Setup Hugging Face API for DeepSeek ---
HUGGINGFACE_API_TOKEN = st.secrets["HUGGINGFACE_API_TOKEN"]

# --- Expanded Sensitive Keyword List (from NSF ban list) ---
sensitive_keywords = {
    word: 1 for word in set([
        # ... [same list as before] ...
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
    prompt = f"""Rewrite this grant proposal to reduce risk from the following terms:
{text}

Flagged terms: {', '.join(flagged_terms)}"""
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300}
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-llm-7b-base",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"] if isinstance(result, list) else result["generated_text"]
    return "[Error generating reworded suggestions from DeepSeek.]"

# --- Streamlit App UI ---
st.set_page_config(page_title="ALIGN: Assessing Language Impact for Grant Narratives", layout="wide")

# Header
st.markdown("""
    <h1 style='color:#6C63FF; font-size: 36px;'>ALIGN: Assessing Language Impact for Grant Narratives</h1>
    <p style='font-size: 16px;'>This tool identifies politically sensitive language in grant narratives and provides risk assessments and suggested rewrites.</p>
""", unsafe_allow_html=True)

agency = st.selectbox("Select Funding Agency Profile", ["NIH", "NSF", "Other"])

# Inputs
col1, col2 = st.columns(2)
with col1:
    title_text = st.text_area("Paste your Title or Abstract", height=100)
with col2:
    summary_text = st.text_area("Paste your Project Summary", height=100)

description_text = st.text_area("Paste your Project Description", height=200)

# Analysis
if st.button("Analyze"):
    combined_text = " ".join([title_text, summary_text, description_text])
    if combined_text.strip():
        flagged = flag_sensitive_terms(combined_text)
        score = compute_risk_score(flagged)
        percentile = estimate_percentile(score)

        # Risk summary
        st.markdown("<h3 style='color:#444;'>Risk Analysis</h3>", unsafe_allow_html=True)
        st.write(f"**Risk Score:** {score}")
        st.markdown("**Risk Score Definition:** Total frequency of flagged terms. Higher scores suggest greater likelihood of scrutiny in politically sensitive reviews.")
        st.write(f"**Estimated Risk Percentile:** {percentile}th percentile")
        st.write(f"**Risk Level:** {risk_level_tag(percentile)}")

        # Results
        if flagged:
            st.markdown("<h3 style='color:#444;'>Flagged Terms</h3>", unsafe_allow_html=True)
            df = pd.DataFrame(flagged.items(), columns=["Term", "Frequency"])
            st.dataframe(df)

            st.markdown("<h3 style='color:#444;'>Highlighted Text</h3>", unsafe_allow_html=True)
            highlighted = highlight_text(combined_text, flagged)
            st.markdown(highlighted, unsafe_allow_html=True)

            st.markdown("<h3 style='color:#444;'>Suggested Rewording</h3>", unsafe_allow_html=True)
            suggestions = suggest_alternatives(combined_text, flagged)
            st.write(suggestions)
        else:
            st.success("No sensitive terms flagged. Low risk detected.")

        # Flowchart classification
        st.markdown("<h3 style='color:#444;'>Flowchart Review Classification</h3>", unsafe_allow_html=True)
        st.write(review_pathway(title_text, summary_text, description_text))
    else:
        st.warning("Please paste content into one or more fields to analyze.")

# --- Footer ---
st.markdown("""
    <hr>
    <p style='font-size: 14px; color: gray;'>
        <strong>Disclaimer:</strong> ALIGN is a prototype research tool and does not represent official guidance from NIH, NSF, or any funding agency. Use this tool to support language reflection and refinement, not as a substitute for professional review.
        <br><br>
        Maintained by <strong>Dr. Kechna Cadet</strong> – Substance Use Epidemiologist
    </p>
""", unsafe_allow_html=True)
