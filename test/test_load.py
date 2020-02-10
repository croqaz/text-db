from tdb import load

JL_FILE_1 = 'test/fixtures/fake_profiles.jl'


def key_func(obj):
    return str(obj)


def key_func_0(obj):
    return 'x'


def validate_func_true(obj):
    return True


def validate_func_false(obj):
    return False


def test_load_files():
    data = load.load_files([JL_FILE_1], config={'keys': key_func})
    assert len(data) == 100


def test_load_json_file():
    data = {}
    load.load_json_file(JL_FILE_1, data, key_func=key_func)
    assert len(data) == 100

    first_value = next(iter(data.values()))
    assert isinstance(first_value, dict)
    assert isinstance(first_value['username'], str)
    assert len(first_value['username'])


def test_load_json_key_zero():
    data = {}
    load.load_json_file(JL_FILE_1, data, key_func=key_func_0)
    assert len(data) == 1
    assert next(iter(data)) == 'x'


def test_load_json_validate_true():
    data = {}
    load.load_json_file(
        JL_FILE_1,
        data,
        key_func=key_func,
        validate_func=validate_func_true,
    )
    assert len(data) == 100


def test_load_json_validate_false():
    data = {}
    load.load_json_file(
        JL_FILE_1,
        data,
        key_func=key_func,
        validate_func=validate_func_false,
    )
    assert len(data) == 0
