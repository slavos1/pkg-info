from pkg_info import __version__ as VERSION


def test_version() -> None:
    assert VERSION is not None
    assert VERSION == "0.1.0"
