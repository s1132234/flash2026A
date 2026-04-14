import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "黃士豪",
  "mail": "s1132234@pu.edu.tw",
  "lab": 777
}

doc_ref = db.collection("靜宜資管2026a").document("flash")
doc_ref.set(doc)
