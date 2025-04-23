from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
import os
from datetime import datetime

# Initialize ChromaDB client and embedding model
chroma_client = chromadb.PersistentClient(path="./chroma")
collection = chroma_client.get_or_create_collection(name="vapi_conversations")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Flask app
app = Flask(__name__)

# === SQLAlchemy Configuration ===
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === Database Model ===
class Conversation(db.Model):
    id = Column(Integer, primary_key=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    recording_url = Column(String(255), nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

# === Create Database Tables ===
with app.app_context():
    db.create_all()

# # === 1. Endpoint to receive user utterance from Vapi and save to ChromaDB ===
# @app.route("/vapi-webhook", methods=["POST"])
# def receive_user_utterance():
#     data = request.json
#     user_text = data.get("user_message")  # Adjust key based on Vapi's actual payload

#     if not user_text:
#         return jsonify({"error": "Missing 'user_message' in payload"}), 400

#     # Generate embedding
#     embedding = embedder.encode(user_text).tolist()

#     # Store in ChromaDB with unique ID
#     doc_id = str(uuid.uuid4())
#     collection.add(
#         documents=[user_text],
#         embeddings=[embedding],
#         ids=[doc_id],
#         metadatas=[{"source": "vapi"}]
#     )

#     return jsonify({"status": "stored", "id": doc_id})

# === 2. Endpoint to retrieve top-k similar messages from ChromaDB ===
@app.route("/get-context", methods=["POST"])
def get_context():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing 'query' in request"}), 400

    # Embed the query
    query_embedding = embedder.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    matched_docs = results.get("documents", [[]])[0]

    return jsonify({
        "context": matched_docs
    })

# === 3. Updated Endpoint to store conversation details from end-of-call report ===
@app.route("/store-conversation", methods=["POST"])
def store_conversation():
    # Expecting the report object directly, not in a list
    data = request.json
    if not isinstance(data, dict):
         return jsonify({"error": "Expected a JSON object payload"}), 400

    message = data.get("message")

    if not message or message.get("type") != "end-of-call-report":
        return jsonify({"error": "Invalid payload structure or type is not 'end-of-call-report'"}), 400

    # Extract relevant information
    artifact = message.get("artifact", {})
    analysis = message.get("analysis", {})

    # Use the pre-formatted transcript if available
    transcript = artifact.get("transcript", message.get("transcript"))
    summary = analysis.get("summary", message.get("summary"))
    recording_url = artifact.get("recordingUrl")
    started_at_str = message.get("startedAt")
    ended_at_str = message.get("endedAt")

    # Convert ISO timestamp strings to datetime objects
    started_at = datetime.fromisoformat(started_at_str.replace("Z", "+00:00")) if started_at_str else None
    ended_at = datetime.fromisoformat(ended_at_str.replace("Z", "+00:00")) if ended_at_str else None

    # Basic validation
    if not transcript:
        return jsonify({"error": "Missing transcript in payload"}), 400

    # Store in SQLAlchemy DB
    new_entry = Conversation(
        transcript=transcript,
        summary=summary,
        recording_url=recording_url,
        started_at=started_at,
        ended_at=ended_at
    )
    db.session.add(new_entry)
    db.session.commit() # Commit here to get the new_entry.id

    # --- Add summary embedding to ChromaDB ---
    if summary: # Only embed if summary exists
        try:
            summary_embedding = embedder.encode(summary).tolist()
            # Use a unique ID, potentially related to the SQL entry
            summary_doc_id = f"summary_{new_entry.id}"
            collection.add(
                documents=[summary],
                embeddings=[summary_embedding],
                ids=[summary_doc_id],
                metadatas=[{"source": "summary", "db_id": new_entry.id}]
            )
        except Exception as e:
            # Log the error, but don't necessarily fail the request
            app.logger.error(f"Failed to embed or store summary for db_id {new_entry.id}: {e}")
            # Optionally return a modified success message indicating partial failure
            # return jsonify({"status": "stored_sql_only", "db_id": new_entry.id, "error": "Failed to store summary embedding"}), 500

    return jsonify({"status": "stored", "db_id": new_entry.id})

# === Start Flask app ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
