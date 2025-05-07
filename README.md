# Grant-Risk-Assessment-App-Streamlit
#  Grant Proposal Risk Scanner

This app is a prototype tool designed to help researchers and grant writers screen their proposals for politically sensitive language that may be flagged by reviewers or pose a risk to funding. 

It uses a keyword-based risk model to:
- Identify terms often flagged in current political climates (e.g., “racism,” “equity,” “disparity”)
- Estimate a *risk score* based on the frequency and weight of these terms
- Assign a *percentile rank* simulating how risky the language is compared to typical submissions

---

##  Features

- Paste your grant proposal text
- Select your target agency (NIH, NSF, Other)
- View:
  - Total risk score
  - Estimated risk percentile
  - List of flagged terms and their frequency

---

##  Try It Online

You can deploy the app using [Streamlit Cloud](https://streamlit.io/cloud) for free. Just upload this repo and select `app.py` as the main file.

---

##  Run Locally

### 1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/grant-risk-scanner.git
cd grant-risk-scanner
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the app:
```bash
streamlit run app.py
```

---

##  Files

- `app.py` – main app file
- `requirements.txt` – dependencies for deployment

---

##  Customization Ideas

- Expand keyword list or load from a dynamic source
- Use NLP embeddings to assess semantic sensitivity
- Add rewrite suggestions for flagged terms

---

##  Disclaimer

This tool is experimental and does **not** guarantee funding outcomes or reflect the policies of any agency. Always consult your program officer and institutional guidance before submitting grant applications.

---

## Contact

For questions or suggestions, feel free to reach out or open an issue in the repository.
