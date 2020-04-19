from search import get_combinations


def test_get_combinations():
    assert len(get_combinations(49)) == 1176
