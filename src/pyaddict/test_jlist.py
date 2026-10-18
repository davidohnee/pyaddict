import pytest

from pyaddict.jlist import JList

data = [{"name": "John", "age": 12}, {"name": "Jane", "age": 14}]


def test_no_chain() -> None:
    assert JList(data).expect(0, dict)
    assert JList(data).expect(1, dict)
    assert JList(data).expect("0", dict)
    with pytest.raises(IndexError):
        JList(data).expect(2, dict)
    with pytest.raises(ValueError):
        JList(data).expect("0.name", dict)


def test_chain() -> None:
    item = JList(data).chain()
    assert item.expect(0, dict)
    assert item.expect(1, dict)
    assert item.expect("0", dict)
    assert item.optional_get(2, dict) is None
    assert item.expect("[0].name", str) == data[0]["name"]
    assert item.optional_get("0.test") is None
    assert item.optional_get("?.b?.d") is None
    assert item.expect("[].name", list) == [x["name"] for x in data]


def test_ensure() -> None:
    jlist = JList(data)
    assert jlist.ensure(0, dict)
    assert jlist.ensure("0", dict)
    assert jlist.ensure(0, str) == ""
    assert jlist.ensure(0, str, "test") == "test"
    assert jlist.ensure(4, str, "test") == "test"
    assert jlist.ensure("[0].name", str) == ""


def test_chain_ensure_cast() -> None:
    jlist = JList(data).chain()
    assert jlist.ensure_cast(0, dict)
    assert jlist.ensure_cast("0", str) == str(data[0])
    assert jlist.ensure_cast("c", str, "test") == "test"
    assert jlist.ensure_cast("4", str, "test") == "test"
    assert jlist.ensure_cast("0.age", str) == "12"
    assert jlist.ensure_cast("0.age", int) == 12
    assert jlist.ensure_cast("0.age", float) == 12.0


def test_chain_ensure() -> None:
    jlist = jlist = JList(data).chain()
    assert jlist.ensure(0, dict)
    assert jlist.ensure("0", str) == ""
    assert jlist.ensure("c", str, "test") == "test"
    assert jlist.ensure("4", str, "test") == "test"
    assert jlist.ensure("0.age", str) == ""
    assert jlist.ensure("0.age", int) == 12
    assert jlist.ensure("0.age", float) == 0.0


def test_optional_get() -> None:
    jlist = JList(data)
    with pytest.raises(ValueError):
        assert jlist.optional_get("a", dict)
    assert jlist.optional_get(0, dict)
    assert jlist.optional_get("0", dict)
    assert jlist.optional_get(2, dict) is None
    assert jlist.optional_get("2", dict) is None
    with pytest.raises(ValueError):
        assert jlist.optional_get("0.age", str)


def test_chain_optional_get() -> None:
    jlist = JList(data).chain()
    assert jlist.optional_get(0, dict)
    assert jlist.optional_get("0", str) is None
    with pytest.raises(KeyError):
        assert jlist.optional_get("0.car.test", str, "test")
    assert jlist.optional_get("c", str, "test") == "test"
    with pytest.raises(TypeError):
        assert jlist.optional_get("c.age", str, "test")
    assert jlist.optional_get("4", str, "test") == "test"
    with pytest.raises(IndexError):
        assert jlist.optional_get("4.age", str, "test")
    assert jlist.optional_get("0.age", str) is None
    assert jlist.optional_get("0.age", int) == 12
    assert jlist.optional_get("0.age", float) is None


def test_expect() -> None:
    jlist = JList(data)
    assert jlist.expect(0, dict)
    assert jlist.expect("0", dict)
    with pytest.raises(IndexError):
        assert jlist.expect(4, dict)
    with pytest.raises(IndexError):
        assert jlist.expect("4", dict)
    with pytest.raises(ValueError):
        assert jlist.expect("c", str) is None
    with pytest.raises(ValueError):
        assert jlist.expect("b", str) is None
    with pytest.raises(ValueError):
        assert jlist.expect("a.b", str) is None


def test_chain_expect() -> None:
    jlist = JList(data).chain()
    assert jlist.expect(0, dict)
    with pytest.raises(TypeError):
        assert jlist.expect("0", str)
    with pytest.raises(TypeError):
        assert jlist.expect("c", str)
    with pytest.raises(IndexError):
        assert jlist.expect("4", str) == "test"
    with pytest.raises(TypeError):
        assert jlist.expect("0.age", str)
    assert jlist.expect("0.age", int) == 12
    with pytest.raises(TypeError):
        assert jlist.expect("0.age", float)


def test_get_list_with_checked_items() -> None:
    jdata = JList([["apple", "banana", 1, 2, 3]])
    mylist = jdata.optional_get(0, list, value_type=str)
    assert mylist == ["apple", "banana", None, None, None]
    mylist = jdata.ensure(0, list, value_type=str)
    assert mylist == ["apple", "banana"]
    mylist = jdata.ensure_cast(0, list, value_type=str)
    assert mylist == ["apple", "banana", "1", "2", "3"]
    with pytest.raises(TypeError):
        mylist = jdata.expect(0, list, value_type=str)


def test_get_dict_with_checked_items() -> None:
    jdata = JList([{"basket": ["apple"], "price": 5, 1: 2}])
    mydict = jdata.optional_get(0, dict, key_type=str, value_type=int)
    assert mydict == {"basket": None, "price": 5}
    mydict = jdata.ensure(0, dict, key_type=str, value_type=int)
    assert mydict == {"price": 5}
    mydict = jdata.ensure_cast(0, dict, key_type=str, value_type=int)
    assert mydict == {"basket": 0, "price": 5, "1": 2}
    with pytest.raises(TypeError):
        mydict = jdata.expect(0, dict, key_type=str, value_type=int)
