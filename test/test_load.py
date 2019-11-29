from tdb import load


def key_func(obj):
    return str(obj)


def validate_func_true(obj):
    return True


def validate_func_false(obj):
    return False


def test_load_json_file():
    data = {}
    load.load_json_file('test/fixtures/fake_profiles.jl', data, key_func=key_func, verbose=False)
    assert len(data) == 100


def test_load_json_validate_true():
    data = {}
    load.load_json_file(
        'test/fixtures/fake_profiles.jl',
        data,
        key_func=key_func,
        validate_func=validate_func_true,
        verbose=False,
    )
    assert len(data) == 100


def test_load_json_validate_false():
    data = {}
    load.load_json_file(
        'test/fixtures/fake_profiles.jl',
        data,
        key_func=key_func,
        validate_func=validate_func_false,
        verbose=False,
    )
    assert len(data) == 0
