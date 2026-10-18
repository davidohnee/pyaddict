"""Common types."""

from typing import Any, Iterable

JObject = dict[str, Any]
JArray = list[Any]


def optional_get[T, K, V](
    value: Any,
    type_: type[T] | None = None,
    default: T | None = None,
    *,
    key_type: type[K] | None = None,
    value_type: type[V] | None = None,
) -> Any | None:
    """Get the value if it matches the target type."""
    if type_ and not isinstance(value, type_):
        return default
    if value is None:
        return default

    if isinstance(value, list) and value_type is not None:
        return [x if isinstance(x, value_type) else None for x in value]

    if isinstance(value, dict) and value_type is not None and key_type is not None:
        return {
            k: v if isinstance(v, value_type) else None
            for k, v in value.items()
            if isinstance(k, key_type)
        }

    return value


def ensure[T, K, V](
    value: Any,
    type_: type[T],
    default: T | None = None,
    *,
    key_type: type[K] | None = None,
    value_type: type[V] | None = None,
) -> Any:
    """Get the value if it matches the target type."""
    if isinstance(value, type_):
        if isinstance(value, list) and value_type is not None:
            return [x for x in value if isinstance(x, value_type)]
        if isinstance(value, dict) and value_type is not None and key_type is not None:
            return {
                k: v
                for k, v in value.items()
                if isinstance(k, key_type) and isinstance(v, value_type)
            }

        return value
    return default or type_()


def ensure_cast[T, K, V](
    value: Any,
    type_: type[T],
    default: T | None = None,
    *,
    key_type: type[K] | None = None,
    value_type: type[V] | None = None,
) -> Any:
    """Get the value and try to cast it to the target type."""

    def _ensure_cast[E](v: Any, t: type[E]) -> E:
        try:
            if isinstance(v, t):
                return v
            return t(v)  # ty: ignore[too-many-positional-arguments]
        except:  # noqa: E722
            return t()

    if isinstance(value, type_):
        if isinstance(value, list) and value_type is not None:
            return [_ensure_cast(x, value_type) for x in value]
        if isinstance(value, dict) and value_type is not None and key_type is not None:
            return {
                _ensure_cast(k, key_type): ensure_cast(v, value_type)
                for k, v in value.items()
            }

        return value
    return _ensure_cast(value, type_)


def expect[T, K, V](
    value: Any,
    type_: type[T],
    *,
    key_type: type[K] | None = None,
    value_type: type[V] | None = None,
) -> Any:
    """Expect the value to be present and of the specified type."""
    if not isinstance(value, type_):
        raise TypeError(f"expected {value} to be {type_}, not {type(value)}")

    def _check_array[E](items: Iterable[Any], type_: type[E], key_name: str) -> None:
        if any(not isinstance(x, type_) for x in items):
            item_types = set([type(x) for x in items])
            raise TypeError(
                f"expected all {key_name} to be {type_}, not one of {item_types}"
            )

    if isinstance(value, list) and value_type is not None:
        _check_array(value, value_type, "items")

    if isinstance(value, dict) and value_type is not None and key_type is not None:
        _check_array(value.keys(), key_type, "keys")
        _check_array(value.values(), value_type, "values")

    return value
