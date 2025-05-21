# ALIGN: Assessing Language Impact for Grant Narratives


This app is a prototype tool designed to help researchers and grant writers screen their proposals for politically sensitive language that may be flagged by reviewers or pose a risk to funding. 

It uses a keyword-based risk model to:
- Identify terms often flagged in current political climates (e.g., “racism,” “equity,” “disparity”)
- Estimate a *risk score* based on the frequency and weight of these terms
- Assign a *percentile rank* simulating how risky the language is compared to typical submissions
- Visualize flagged words in context
- Flowchart-based classification logic
- (Coming soon) LLM-powered rewrites for flagged language

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

[Launch ALIGN on Streamlit Cloud](https://grant-risk-assessment-app-app-yacfwhbnxkthqtp2mepqnx.streamlit.app)


##  Run Locally

```bash
git clone https://github.com/kcadet91/ALIGN-App.git
cd ALIGN-App
pip install -r requirements.txt
streamlit run app_v2.py

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
