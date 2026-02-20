from utils.validation import (
    check_file_integrity,
    assign_confidence_score,
    calculate_md5,
)
import os


def test_md5():
    data = b"testdata"
    assert calculate_md5(data) == "f8b1ad6ca1965b93569dd30ce7eaf8fa"


def test_confidence_score():
    # A random block won't pass integrity or have JPEG header
    garbage = os.urandom(512)
    score1 = assign_confidence_score(garbage)
    assert score1 == 0.0

    # Dummy JPEG header without valid body will get 15%
    dummy_jpeg_header = b"\xff\xd8\xff\xe0\x00" + os.urandom(500)
    score2 = assign_confidence_score(dummy_jpeg_header)
    assert score2 == 15.0
