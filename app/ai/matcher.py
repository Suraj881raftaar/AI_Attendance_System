"""
Face Embedding Matcher Decision Engine for AI-Enabled Smart Attendance System.
Compares query embeddings against database enrolled embeddings using Cosine Similarity.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from app.config import FACE_MATCH_THRESHOLD
from app.database import get_db_connection
from app.ai.embedder import SFaceRecognizer

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """
    Structured output of face matching decision.
    """
    is_known: bool
    student_id: Optional[int]
    student_code: Optional[str]
    student_name: Optional[str]
    similarity_score: float
    threshold: float
    bbox: Tuple[int, int, int, int]  # Bounding box of recognized face


class FaceMatcher:
    """
    Decision engine for matching face embeddings against enrolled database records.
    """

    def __init__(
        self,
        embedder: Optional[SFaceRecognizer] = None,
        threshold: float = FACE_MATCH_THRESHOLD,
        db_path: Optional[Union[str, Path]] = None,
    ):
        self.embedder = embedder or SFaceRecognizer()
        self.threshold = threshold
        self.db_path = db_path

    def load_enrolled_embeddings(self, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        Fetch all active enrolled face embeddings for active students from SQLite.
        
        Returns:
            List[Dict]: Items containing student_id, student_code, name, and embedding numpy array.
        """
        effective_db = db_path or self.db_path
        query = """
            SELECT f.student_id, f.encoding_data, f.model_identifier, s.student_id as student_code, s.name as student_name, s.status as student_status
            FROM face_data f
            JOIN students s ON f.student_id = s.id
            WHERE f.status = 'active' AND s.status = 'active'
        """
        results: List[Dict[str, Any]] = []

        try:
            with get_db_connection(effective_db) as conn:
                rows = conn.execute(query).fetchall()
                for row in rows:
                    try:
                        raw_json = row["encoding_data"]
                        vector_list = json.loads(raw_json)
                        vector = np.array(vector_list, dtype=np.float32)

                        # Ensure normalization
                        norm = np.linalg.norm(vector)
                        if norm > 0:
                            vector = vector / norm

                        results.append({
                            "id": row["student_id"],
                            "student_code": row["student_code"],
                            "student_name": row["student_name"],
                            "embedding": vector,
                            "model_identifier": row["model_identifier"],
                        })
                    except Exception as parse_err:
                        logger.error(f"Error parsing encoding data for student ID {row['student_id']}: {parse_err}")
            return results
        except Exception as e:
            logger.error(f"Error loading enrolled embeddings from database: {e}")
            return []

    def match_embedding(
        self,
        query_embedding: np.ndarray,
        bbox: Tuple[int, int, int, int] = (0, 0, 0, 0),
        enrolled_cache: Optional[List[Dict[str, Any]]] = None,
        db_path: Optional[Union[str, Path]] = None,
    ) -> MatchResult:
        """
        Compare query feature embedding against enrolled student embeddings.
        
        :param query_embedding: 128D query float32 numpy array.
        :param bbox: Face bounding box tuple.
        :param enrolled_cache: Optional pre-loaded enrolled embeddings list for batch efficiency.
        :param db_path: Optional SQLite database path.
        :return: MatchResult object.
        """
        if query_embedding is None or len(query_embedding) == 0:
            return MatchResult(
                is_known=False, student_id=None, student_code=None, student_name=None,
                similarity_score=0.0, threshold=self.threshold, bbox=bbox
            )

        enrolled = enrolled_cache if enrolled_cache is not None else self.load_enrolled_embeddings(db_path=db_path)
        if not enrolled:
            return MatchResult(
                is_known=False, student_id=None, student_code=None, student_name=None,
                similarity_score=0.0, threshold=self.threshold, bbox=bbox
            )

        best_score = -1.0
        best_student: Optional[Dict[str, Any]] = None

        for rec in enrolled:
            score = self.embedder.compute_cosine_similarity(query_embedding, rec["embedding"])
            if score > best_score:
                best_score = score
                best_student = rec

        if best_student is not None and best_score >= self.threshold:
            return MatchResult(
                is_known=True,
                student_id=best_student["id"],
                student_code=best_student["student_code"],
                student_name=best_student["student_name"],
                similarity_score=float(best_score),
                threshold=self.threshold,
                bbox=bbox,
            )
        else:
            return MatchResult(
                is_known=False,
                student_id=best_student["id"] if (best_student and best_score > 0) else None,
                student_code=best_student["student_code"] if (best_student and best_score > 0) else None,
                student_name="Unknown Face",
                similarity_score=float(max(0.0, best_score)),
                threshold=self.threshold,
                bbox=bbox,
            )
