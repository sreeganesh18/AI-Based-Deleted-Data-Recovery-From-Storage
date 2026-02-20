from utils.validation import (
    assign_confidence_score,
    calculate_md5,
)
import os


def test_md5():
    data = b"testdata"
    assert calculate_md5(data) == "ef654c40ab4f1747fc699915d4f70902"


def test_confidence_score():
    # A random block won't pass integrity or have JPEG header
    garbage = os.urandom(512)
    score1 = assign_confidence_score(garbage)
    assert score1 == 0.0

    # Dummy JPEG header without valid body will get 15%
    dummy_jpeg_header = b"\xff\xd8\xff\xe0\x00" + os.urandom(500)
    score2 = assign_confidence_score(dummy_jpeg_header)
    assert score2 == 15.0
