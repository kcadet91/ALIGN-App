import streamlit as st
import re
import pandas as pd
from collections import Counter

# --- Expanded Sensitive Keyword List (from NSF ban list) ---
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
    score = sum(sensitive_keywords[word] * count for word, count in flagged_terms.items())
    return score

def estimate_percentile(score):
    if score == 0:
        return 1
    elif score < 5:
        return 25
    elif score < 10:
        return 50
    elif score < 20:
        return 75
    else:
        return 90

# --- Streamlit App ---
st.set_page_config(page_title="Grant Risk Scanner", layout="wide")
st.title("🧠 Grant Proposal Risk Scanner")
st.markdown("This tool flags politically sensitive language and estimates the risk percentile based on current climate.")

agency = st.selectbox("Select Funding Agency Profile", ["NIH", "NSF", "Other"])
grant_text = st.text_area("Paste your grant text here", height=300)

if st.button("Analyze"):
    if grant_text:
        flagged = flag_sensitive_terms(grant_text)
        score = compute_risk_score(flagged)
        percentile = estimate_percentile(score)

        st.subheader("📊 Risk Analysis")
        st.write(f"**Risk Score:** {score}")
        st.write(f"**Estimated Risk Percentile:** {percentile}th percentile")

        if flagged:
            st.subheader("🚩 Flagged Terms")
            df = pd.DataFrame(flagged.items(), columns=["Term", "Frequency"])
            st.dataframe(df)
        else:
            st.success("No sensitive terms flagged. Low risk detected.")
    else:
        st.warning("Please paste some text to analyze.")
