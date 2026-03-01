import pytest
import os


def pytest_addoption(parser):
    parser.addoption("--parallel", action="store_true", help="Run parallel tests")


@pytest.fixture(scope="session")
def dummy_disk_image(tmp_path_factory):
    """
    Creates a dummy disk image file (.dd) with a simulated JPEG file embedded inside.
    """
    img_path = tmp_path_factory.mktemp("data") / "dummy.dd"
    with open(img_path, "wb") as f:
        # Write 1000 bytes of garbage
        f.write(os.urandom(1000))
        # Write JPEG header FFD8FFE0 ...
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        # Write random image data
        f.write(os.urandom(800))
        # Write JPEG footer
        f.write(b"\xff\xd9")
        # Write more garbage
        f.write(os.urandom(1000))
    return str(img_path)
