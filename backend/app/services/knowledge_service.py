"""Knowledge Database service representing the Vector DB / Knowledge Base in the architecture.

Retrieves grounded context documents for safe prompts before dispatching to the LLM.
"""

import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

DEFAULT_KNOWLEDGE_DOCS = [
    {
        "id": "KB-001",
        "title": "Academic Attendance Policy",
        "content": "A minimum of 75% attendance is required in each course to be eligible for end-semester examinations. Medical leave exemptions must be submitted within 7 working days with verified documentation."
    },
    {
        "id": "KB-002",
        "title": "Course Grading and Credits",
        "content": "The grading system follows a 10-point SGPA/CGPA scale. Grade S is 10 points (>=90%), Grade A is 9 points (>=80%), Grade B is 8 points (>=70%), Grade C is 7 points (>=60%), Grade P is 6 points (Passing), and Grade F is Failed."
    },
    {
        "id": "KB-003",
        "title": "Campus IT and Network Usage Policy",
        "content": "Campus Wi-Fi and computing labs are strictly for academic and research purposes. Network port scanning, credential sniffing, unauthorized proxying, or circumvention of campus firewalls constitutes a serious disciplinary violation."
    },
    {
        "id": "KB-004",
        "title": "Final Year Capstone Project Guidelines",
        "content": "Final year projects must undergo three milestone evaluations: Zeroth Review (problem formulation and literature survey), First Review (architecture and module design), and Final Defense (demonstration and thesis submission)."
    },
    {
        "id": "KB-005",
        "title": "Examination Malpractice & Ethics",
        "content": "Strict zero-tolerance policy against academic dishonesty, plagiarism in project reports, or tampering with university examination portal data."
    }
]


class KnowledgeService:
    """Vector / Semantic retrieval engine over the system's Knowledge Database."""

    def __init__(self, documents: List[Dict[str, str]] = None):
        self.documents = documents or DEFAULT_KNOWLEDGE_DOCS
        self.vectorizer = TfidfVectorizer(stop_words="english")
        doc_texts = [d["title"] + " " + d["content"] for d in self.documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(doc_texts)

    def retrieve_context(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """Retrieve the most relevant knowledge records for a given user query."""
        try:
            q_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self.tfidf_matrix)[0]
            top_indices = np.argsort(sims)[::-1][:top_k]

            results = []
            for idx in top_indices:
                if sims[idx] > 0.05:  # Similarity threshold
                    results.append({
                        **self.documents[idx],
                        "similarity_score": round(float(sims[idx]), 3)
                    })
            return results
        except Exception as e:
            logger.error(f"Error in Knowledge DB retrieval: {e}")
            return []


knowledge_service = KnowledgeService()
