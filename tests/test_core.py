from PlamodelReleaseDate.core import get_release_date


def test_get_release_date():
    assert get_release_date("X") == "1970-01-01"
