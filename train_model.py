import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import pandas as pd

df = pd.read_excel("training_data.xlsx")

df = df[df["text"].str.len() > 50]

X = df["text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2), 
        stop_words="english" 
    )),
    ("clf", LogisticRegression(max_iter=1000))
])

print("Training model...")
model.fit(X_train, y_train)

print("\nEvaluation on test set:")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save the model to use it on Lambda
joblib.dump(model, "document_classifier.pkl")
print("\nSaved model as document_classifier.pkl")
