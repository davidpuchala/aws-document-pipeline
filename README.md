# Automated Document Processing & Routing System

**AWS Cloud Computing Final Project · ESADE Business School**  
Team: David Puchala · Giorgio Fiorentino · Jakob Kohrgruber · María Angélica Mora Zamora · Warren Yuqing Liu

---

## Overview

Companies in document-heavy industries (legal, healthcare, finance) receive hundreds of documents daily — contracts, invoices, forms — arriving in mixed formats via email, uploads, and scans. Manual sorting is slow, error-prone, and wastes skilled staff time.

This project builds a **fully serverless, ML-driven document classification and routing pipeline on AWS**. A user uploads a document through a web dashboard; the system automatically extracts its text, classifies it, stores it in the appropriate S3 destination, records metadata to DynamoDB, and sends an email notification via SNS — all without human intervention.

---

## Architecture

```
User uploads document (PDF/PNG/JPG)
        │
        ▼
  API Gateway (REST)
        │
        ▼
  Lambda: Ingest
  → Stores raw file to S3 incoming/
        │
        ▼
  Lambda: Classify
  → Extracts text via AWS Textract
  → Loads TF-IDF + Logistic Regression model from S3
  → Predicts document type (invoice / contract / form / manual_review)
  → Routes file to typed S3 folder (e.g. processed/invoices/)
  → Writes metadata + confidence score to DynamoDB
        │
        ▼
  DynamoDB Streams
        │
        ▼
  Lambda: Notify
  → Publishes classification result to SNS
  → Triggers email notification to recipient
        │
        ▼
  Frontend Dashboard
  → Polls API Gateway for DynamoDB status
  → Displays classification, confidence score, S3 destination, metadata
```

**AWS Services used:** Lambda · S3 · Textract · DynamoDB (+ Streams) · SNS · API Gateway

---

## Machine Learning Model

### Approach

We use a **TF-IDF + Logistic Regression** pipeline built with scikit-learn. This was chosen over more complex alternatives (e.g. SageMaker-hosted models) because:
- It delivers high accuracy on keyword-heavy document text
- It is lightweight enough to be loaded directly inside a Lambda function
- It requires no external ML services, keeping the architecture simple and costs near-zero

### Training Data

Documents were sourced from open datasets covering legal contracts, invoices, and forms in PDF, PNG, and JPG format. Text was extracted using `pdfplumber` (PDFs) and `pytesseract` (images).

| Label    | Documents |
|----------|-----------|
| Invoice  | 432       |
| Form     | 198       |
| Contract | included  |
| **Total**| **630+**  |

### Model Pipeline

```python
Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words="english"
    )),
    ("clf", LogisticRegression(max_iter=1000))
])
```

The trained model is serialised with `joblib` and stored in S3, where it is loaded at Lambda cold-start.

---

## Repository Structure

```
├── build_dataset.py        # Text extraction from PDFs/images → training_data.csv
├── train_model.py          # Model training + evaluation + export to .pkl
├── document_classifier.pkl # Serialised TF-IDF + Logistic Regression model
├── training_data.csv       # Extracted text dataset with labels
├── training_data.xlsx      # Same dataset in Excel format
└── dashboard.html          # Frontend: upload interface + live classification feed
```

---

## Dashboard

The frontend (`dashboard.html`) is a single-file HTML/JS application that:

- Accepts document uploads (PDF, PNG, JPG) and sends them to API Gateway as base64
- Displays a real-time processing log
- Polls the status API every 3 seconds until DynamoDB confirms classification
- Shows per-document details: classification label, confidence score, S3 destination path, DynamoDB PK/SK metadata

Document types are colour-coded: **Invoice** (blue) · **Contract** (purple) · **Form** (amber) · **Manual Review** (grey)

---

## Performance & Cost

| Metric | Value |
|--------|-------|
| End-to-end inference latency | ~7.6 seconds |
| Cost per inference | ~$0.000127 |
| Cost at 100,000 inferences | ~$12.70 |
| Cost at 1,000,000 inferences | ~$127.00 |

Latency reflects the full async pipeline (multiple Lambda steps, DynamoDB Streams, SNS triggers, cold starts) — not model inference time alone, which is negligible.

**Real-world estimate:** a mid-sized law firm processing ~100,000 documents per year would incur roughly **$12.70/year** in inference costs.

---

## Limitations & Future Work

- Model trained on a limited dataset; performance on edge cases is not guaranteed
- No automated handling of data/model drift
- Pipeline could be simplified to a single Lambda function for lower latency
- Future additions: multilingual preprocessing (Textract supports multiple languages), audit trail routing for compliance, multi-channel input (email ingestion, WhatsApp chatbot)

---

## Local Setup

**1. Build the dataset**
```bash
pip install pdfplumber pytesseract pillow pandas
python build_dataset.py
```
Reads documents from local folders (`Contracts/`, `Forms/`, `Invoice/`) and outputs `training_data.csv`.

**2. Train the model**
```bash
pip install scikit-learn pandas joblib openpyxl
python train_model.py
```
Outputs `document_classifier.pkl`.

**3. Deploy**  
Upload `document_classifier.pkl` to your S3 bucket and reference its path in the classification Lambda function.
