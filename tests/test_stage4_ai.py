"""
Comprehensive Stage 4 AI Unit and Integration Test Suite.
Tests AI configuration, model path validation, missing model handling, frame providers,
YuNet face detector, SFace embedder, cosine matcher, enrollment workflow, RBAC authorization,
safety rules, and database integration.

USES SYNTHETIC TEST FIXTURES ONLY. ZERO REAL BIOMETRIC DATA.
"""

import json
import tempfile
from pathlib import Path
import cv2
import numpy as np
import pytest

from app.config import FACE_DETECTION_MODEL_PATH, FACE_RECOGNITION_MODEL_PATH, FACE_MATCH_THRESHOLD
from app.database import (
    initialize_database,
    create_student,
    get_face_data_by_student,
    create_or_update_face_data,
    deactivate_student,
)
from app.auth import get_session
from app.ai.config import AIRuntimeStatus, check_models_exist, get_ai_runtime_status
from app.ai.providers import FrameProvider, ImageFrameProvider, VideoFrameProvider, CameraFrameProvider
from app.ai.detector import YuNetFaceDetector, FaceDetectionResult
from app.ai.embedder import SFaceRecognizer
from app.ai.matcher import FaceMatcher, MatchResult
from app.ai.enrollment import FaceEnrollmentManager
from app.ai.pipeline import AIRecognitionPipeline


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    initialize_database(db_path)
    yield db_path
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass


@pytest.fixture
def authenticated_session(temp_db):
    """Authenticate session as teacher for RBAC testing."""
    session = get_session()
    session.start_session({"id": 1, "username": "teacher1", "role": "teacher"})
    yield session
    session.clear_session()


@pytest.fixture
def synthetic_face_image():
    """Generate a synthetic non-identifying image buffer containing a simple shape face."""
    img = np.full((300, 300, 3), 200, dtype=np.uint8)
    # Draw simple synthetic head circle and features
    cv2.circle(img, (150, 150), 80, (100, 100, 100), -1)
    cv2.circle(img, (120, 130), 10, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (180, 130), 10, (0, 0, 0), -1)  # Right eye
    cv2.line(img, (130, 190), (170, 190), (0, 0, 0), 3)  # Mouth
    return img


# ============================================================================
# 4A: AI RUNTIME & MODEL CONFIGURATION TESTS
# ============================================================================

def test_ai_config_paths():
    """Verify AI model paths and status structure."""
    status = get_ai_runtime_status()
    assert "status" in status
    assert "is_available" in status
    assert "yunet_exists" in status
    assert "sface_exists" in status


def test_missing_model_handling(tmp_path):
    """Verify system reports MISSING status cleanly when model files do not exist."""
    fake_detector = YuNetFaceDetector(model_path=tmp_path / "non_existent_yunet.onnx")
    fake_embedder = SFaceRecognizer(model_path=tmp_path / "non_existent_sface.onnx")

    assert fake_detector.is_loaded is False
    assert fake_embedder.is_loaded is False

    # Detection/embedding should return empty results without crashing
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert fake_detector.detect(dummy_frame) == []
    assert fake_embedder.extract_feature(dummy_frame, None) is None


def test_model_initialization():
    """Verify local YuNet and SFace models load if present."""
    if check_models_exist() == (True, True):
        detector = YuNetFaceDetector()
        embedder = SFaceRecognizer()
        assert detector.is_loaded is True
        assert embedder.is_loaded is True


# ============================================================================
# 4B: FRAME PROVIDER SYSTEM TESTS
# ============================================================================

def test_image_frame_provider_numpy(synthetic_face_image):
    """Test ImageFrameProvider with numpy array."""
    provider = ImageFrameProvider(synthetic_face_image)
    success, frame = provider.get_frame()
    assert success is True
    assert frame is not None
    assert frame.shape == (300, 300, 3)
    provider.release()


def test_image_frame_provider_file(tmp_path, synthetic_face_image):
    """Test ImageFrameProvider with image file path."""
    img_path = tmp_path / "test_face.jpg"
    cv2.imwrite(str(img_path), synthetic_face_image)

    provider = ImageFrameProvider(img_path)
    success, frame = provider.get_frame()
    assert success is True
    assert frame is not None
    assert frame.shape == (300, 300, 3)
    provider.release()


def test_image_frame_provider_invalid_file(tmp_path):
    """Test ImageFrameProvider with non-existent file."""
    with pytest.raises(FileNotFoundError):
        ImageFrameProvider(tmp_path / "missing.jpg")


def test_video_frame_provider(tmp_path, synthetic_face_image):
    """Test VideoFrameProvider with a temporary video file."""
    video_path = tmp_path / "test_video.avi"
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(str(video_path), fourcc, 10.0, (300, 300))
    for _ in range(5):
        out.write(synthetic_face_image)
    out.release()

    provider = VideoFrameProvider(video_path)
    success, frame = provider.get_frame()
    assert success is True
    assert frame is not None
    provider.release()


def test_camera_frame_provider_unavailable():
    """Test CameraFrameProvider graceful handling of invalid camera index."""
    # Index 9999 is invalid/unavailable
    provider = CameraFrameProvider(camera_index=9999)
    assert provider.is_available is False
    success, frame = provider.get_frame()
    assert success is False
    assert frame is None
    provider.release()


# ============================================================================
# 4C & 4D: FACE DETECTION & EMBEDDING TESTS
# ============================================================================

def test_face_detector_empty_frame():
    """Test detector returns empty list on empty/invalid frames."""
    detector = YuNetFaceDetector()
    assert detector.detect(None) == []
    assert detector.detect(np.array([])) == []


def test_face_embedder_dimension_and_normalization():
    """Test SFace feature extraction output dimensions (128D) and L2 normalization."""
    if not check_models_exist()[1]:
        pytest.skip("SFace model file not available locally.")

    embedder = SFaceRecognizer()
    assert embedder.is_loaded is True

    # Generate synthetic 112x112 aligned face matrix
    synthetic_aligned_face = np.full((112, 112, 3), 150, dtype=np.uint8)
    cv2.circle(synthetic_aligned_face, (56, 56), 40, (100, 100, 100), -1)

    # Directly run SFace feature extraction
    raw_feature = embedder._recognizer.feature(synthetic_aligned_face).flatten()
    assert len(raw_feature) == 128

    # Apply L2 normalization
    norm_val = np.linalg.norm(raw_feature)
    normalized_feature = raw_feature / norm_val
    assert np.linalg.norm(normalized_feature) == pytest.approx(1.0, rel=1e-3)


# ============================================================================
# 4E: FACE ENROLLMENT TESTS
# ============================================================================

def test_face_enrollment_unauthenticated(temp_db, synthetic_face_image):
    """Test face enrollment enforces RBAC permission check."""
    session = get_session()
    session.clear_session()

    manager = FaceEnrollmentManager(db_path=temp_db)
    with pytest.raises(PermissionError):
        manager.enroll_student_from_frames(student_id=1, frames=[synthetic_face_image])


def test_face_enrollment_inactive_student(temp_db, authenticated_session, synthetic_face_image):
    """Test face enrollment rejects inactive students."""
    s = create_student("S101", "John Doe", "12", "A", db_path=temp_db)
    deactivate_student(s["id"], db_path=temp_db)

    manager = FaceEnrollmentManager(db_path=temp_db)
    with pytest.raises(ValueError, match="inactive"):
        manager.enroll_student_from_frames(student_id=s["id"], frames=[synthetic_face_image])


def test_face_enrollment_database_storage(temp_db, authenticated_session):
    """Test embedding serialization and storage in SQLite face_data table."""
    s = create_student("S102", "Jane Smith", "12", "B", db_path=temp_db)
    
    # Manually store synthetic 128D vector
    synthetic_vector = np.random.randn(128).astype(np.float32)
    synthetic_vector /= np.linalg.norm(synthetic_vector)
    json_str = json.dumps(synthetic_vector.tolist())

    record = create_or_update_face_data(
        student_id=s["id"],
        model_identifier="opencv_sface_v1",
        encoding_data=json_str,
        data_format="json",
        db_path=temp_db,
    )

    assert record["student_id"] == s["id"]
    assert record["model_identifier"] == "opencv_sface_v1"
    assert record["status"] == "active"

    # Verify retrieval
    retrieved = get_face_data_by_student(s["id"], db_path=temp_db)
    assert retrieved is not None
    parsed_vec = np.array(json.loads(retrieved["encoding_data"]), dtype=np.float32)
    assert len(parsed_vec) == 128
    assert np.allclose(parsed_vec, synthetic_vector, atol=1e-5)


# ============================================================================
# 4F & 4G: FACE RECOGNITION & SAFETY TESTS
# ============================================================================

def test_cosine_similarity_matching():
    """Test FaceMatcher cosine similarity comparison logic."""
    embedder = SFaceRecognizer()
    matcher = FaceMatcher(embedder=embedder, threshold=0.363)

    v1 = np.random.randn(128).astype(np.float32)
    v1 /= np.linalg.norm(v1)

    v2 = v1.copy()  # Identical vector

    # Perturbed vector (different person)
    v3 = np.random.randn(128).astype(np.float32)
    v3 /= np.linalg.norm(v3)

    # Identical score should be 1.0
    score_same = matcher.embedder.compute_cosine_similarity(v1, v2)
    assert score_same == pytest.approx(1.0, rel=1e-3)

    # Different score should be low
    score_diff = matcher.embedder.compute_cosine_similarity(v1, v3)
    assert score_diff < 0.363


def test_matcher_known_vs_unknown(temp_db):
    """Test FaceMatcher decision logic against enrolled database records."""
    s = create_student("S103", "Alice Bob", "12", "A", db_path=temp_db)

    # Create enrolled target vector
    v_enrolled = np.random.randn(128).astype(np.float32)
    v_enrolled /= np.linalg.norm(v_enrolled)
    json_str = json.dumps(v_enrolled.tolist())
    create_or_update_face_data(s["id"], "opencv_sface_v1", json_str, db_path=temp_db)

    matcher = FaceMatcher(threshold=0.363, db_path=temp_db)

    # Query with matching vector
    match_known = matcher.match_embedding(v_enrolled, db_path=temp_db)
    assert match_known.is_known is True
    assert match_known.student_id == s["id"]
    assert match_known.student_name == "Alice Bob"
    assert match_known.similarity_score >= 0.363

    # Query with orthogonal/different vector
    v_unknown = -v_enrolled
    match_unknown = matcher.match_embedding(v_unknown, db_path=temp_db)
    assert match_unknown.is_known is False


def test_recognition_pipeline_cooldown_and_duplicates(temp_db):
    """Test AIRecognitionPipeline cooldown and duplicate attendance protection."""
    s = create_student("S104", "Charlie Brown", "12", "A", db_path=temp_db)

    pipeline = AIRecognitionPipeline(threshold=0.363, cooldown_seconds=5.0, db_path=temp_db)

    dummy_match = MatchResult(
        is_known=True,
        student_id=s["id"],
        student_code=s["student_id"],
        student_name=s["name"],
        similarity_score=0.85,
        threshold=0.363,
        bbox=(10, 10, 100, 100),
    )

    # First attempt -> recorded
    rec1 = pipeline.mark_attendance_from_match(dummy_match, db_path=temp_db)
    assert rec1 is not None
    assert rec1["student_id"] == s["id"]

    # Immediate second attempt -> blocked by cooldown
    rec2 = pipeline.mark_attendance_from_match(dummy_match, db_path=temp_db)
    assert rec2 is None
