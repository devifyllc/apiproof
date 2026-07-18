"""Basic test to verify pytest setup is working correctly."""


def test_pytest_setup():
    """Verify pytest is configured and working."""
    assert True


def test_python_version():
    """Verify Python version meets requirements (3.8+)."""
    import sys
    
    version_info = sys.version_info
    assert version_info.major == 3
    assert version_info.minor >= 8, f"Python 3.8+ required, got {version_info.major}.{version_info.minor}"
