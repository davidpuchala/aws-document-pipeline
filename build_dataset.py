import os
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd

BASE_DIR = "/Users/mariamorazamora/Downloads/CC"

CLASS_FOLDERS = {
    "contract": "Contracts",
    "form": "Forms",
    "invoice": "Invoice",
}

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_image(path):
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return text

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in [".pdf"]:
        return extract_text_from_pdf(path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(path)
    else:
        print(f"Skipping unsupported file type: {path}")
        return ""

def build_dataset():
    rows = []

    for label, folder_name in CLASS_FOLDERS.items():
        folder_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.isdir(folder_path):
            print(f"WARNING: folder not found: {folder_path}")
            continue

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue

            print(f"Processing {file_path} as {label}...")
            text = extract_text(file_path)
            if text.strip():
                rows.append({
                    "text": text,
                    "label": label,
                    "filename": filename
                })

    df = pd.DataFrame(rows)
    print(f"\nTotal documents processed: {len(df)}")
    df.to_csv("training_data.csv", index=False)
    print("Saved training_data.csv")

if __name__ == "__main__":
    build_dataset()
