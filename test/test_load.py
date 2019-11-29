from tdb import load


def key_func(obj):
    return str(obj)


def validate_func(obj):
    return True


def test_load_json_file():
    data = {}
    load.load_json_file(
        'test/fixtures/fake_profiles.jl',
        data,
        key_func=key_func,
        validate_func=validate_func,
        verbose=False,
    )
    assert len(data) == 100
