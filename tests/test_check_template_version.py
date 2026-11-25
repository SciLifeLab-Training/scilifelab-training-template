import pytest

from scripts.check_template_version import is_newer


@pytest.mark.parametrize(
    ("latest", "current", "expected"),
    [
        ("1.2.0", "1.1.0", True),
        ("v1.2.0", "1.1.0", True),
        ("1.10.0", "1.9.0", True),
        ("2.0.0", "1.9.9", True),
        ("1.0.0", "1.0.0-alpha", True),
        ("1.0.0-beta", "1.0.0-alpha", True),
        ("1.2", "1.2.0", False),
        ("1.1.0", "1.1.0", False),
        ("1.1.0", "1.2.0", False),
        ("1.0.0-alpha", "1.0.0", False),
    ],
)
def test_is_newer(latest: str, current: str, expected: bool) -> None:
    assert is_newer(latest, current) is expected
