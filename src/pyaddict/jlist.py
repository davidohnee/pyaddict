"""type-safe list helper."""

from typing import Any, overload

from pyaddict.chain import ChainLink, traverse
from pyaddict.common import JArray, ensure, ensure_cast, expect, optional_get


class JList(list):
    """Type-safe list helper."""

    __slots__ = ("_data", "_chainable")

    def __init__(self, data: JArray | None = None, *, chainable: bool = False) -> None:
        """Create a new type-safe list helper."""
        self._data = data or {}
        self._chainable = chainable
        super().__init__(self._data)

    def _get_item(self, key: int | str, *, optional: bool = False) -> Any | None:
        if self._chainable:
            return traverse(
                self._data,
                ChainLink.create_chain(
                    str(key), allow_first_int=True, last_optional=optional
                ),
            )
        key = int(key)
        if 0 <= key < len(self._data):
            return self._data[int(key)]
        if optional:
            return None
        raise IndexError()

    def chain(self) -> "JList":
        """
        Enable chaining (nested access).

        Returns:
            self

        """
        self._chainable = True
        return self

    def no_chain(self) -> "JList":
        """
        Disable chaining (nested access).

        Returns:
            self

        """
        self._chainable = False
        return self

    @overload
    def optional_get(self, key: int | str) -> Any | None: ...

    @overload
    def optional_get[T](self, key: int | str, type_: type[T], default: T) -> T: ...

    @overload
    def optional_get[T](
        self, key: int | str, type_: type[T], default: T | None = None
    ) -> T | None: ...

    @overload
    def optional_get[V](
        self,
        key: int | str,
        type_: type[list],
        default: list[V] | None = None,
        *,
        value_type: type[V],
    ) -> list[V | None] | None: ...

    @overload
    def optional_get[K, V](
        self,
        key: int | str,
        type_: type[dict],
        default: dict[K, V] | None = None,
        *,
        key_type: type[K],
        value_type: type[V],
    ) -> dict[K, V | None] | None: ...

    def optional_get[T, K, V](
        self,
        key: int | str,
        type_: type[T] | None = None,
        default: T | None = None,
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> Any | None:
        """
        Get the value if it matches the target type.

        Args:
            key: path to the `value`.
            type_: expected type of `value`.
            default: default value to use.
            key_type: expected type of all keys of `value`,
                if `value` is a `dict`, and `key_type` is not `None`.
            value_type: expected type of all values of `value`,
                if `value` is a `dict` or `list`, and `value_type` is not `None`.

        Returns:
            `value` at `key`: if `value` found and has the expected `type`.
            `default`: if `value` not found or not of the expected `type`.
            `None`: if `value` not found and no `default` provided.

        Raises:
            `KeyError`: if `chaining` is enabled and the `key`
                (unless it is optional or the last one) cannot be found.
            `IndexError`: if `chaining` is enabled and the `index`
                (unless it is optional or the last one) is out of range.
            `TypeError`: if `chaining` is enabled and a `list` is indexed with a string.

        """
        value = self._get_item(key, optional=True)
        return optional_get(
            value, type_, default, key_type=key_type, value_type=value_type
        )

    @overload
    def ensure[T](self, key: int | str, type_: type[T]) -> T: ...

    @overload
    def ensure[T](self, key: int | str, type_: type[T], default: T) -> T: ...

    @overload
    def ensure[V](
        self,
        key: int | str,
        type_: type[list],
        default: list[V] | None = None,
        *,
        value_type: type[V],
    ) -> list[V]: ...

    @overload
    def ensure[K, V](
        self,
        key: int | str,
        type_: type[dict],
        default: dict[K, V] | None = None,
        *,
        key_type: type[K],
        value_type: type[V],
    ) -> dict[K, V]: ...

    def ensure[T, K, V](
        self,
        key: int | str,
        type_: type[T],
        default: T | None = None,
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> T:
        """
        Get the value if it matches the target type.

        Args:
            key: path to the `value`.
            type_: expected type of `value`.
            default: default value to use.
            key_type: expected type of all keys of `value`,
                if `value` is a `dict`, and `key_type` is not `None`.
            value_type: expected type of all values of `value`,
                if `value` is a `dict` or `list`, and `value_type` is not `None`.

        Returns:
            `value` at `key`: if `value` found and has the expected `type`.
            `default`: if `value` not found or not of the expected `type`.
            `type()`: if `value` not found and no `default` provided.

        """
        try:
            value = self._get_item(key)
            return ensure(
                value, type_, default, key_type=key_type, value_type=value_type
            )
        except:  # noqa: E722
            return default or type_()

    @overload
    def ensure_cast[T](self, key: int | str, type_: type[T]) -> T: ...

    @overload
    def ensure_cast[T](self, key: int | str, type_: type[T], default: T) -> T: ...

    @overload
    def ensure_cast[V](
        self,
        key: int | str,
        type_: type[list],
        default: list[V] | None = None,
        *,
        value_type: type[V],
    ) -> list[V]: ...

    @overload
    def ensure_cast[K, V](
        self,
        key: int | str,
        type_: type[dict],
        default: dict[K, V] | None = None,
        *,
        key_type: type[K],
        value_type: type[V],
    ) -> dict[K, V]: ...

    def ensure_cast[T, K, V](
        self,
        key: int | str,
        type_: type[T],
        default: T | None = None,
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> Any:
        """
        Get the `value` and try to cast it to the target type.

        Args:
            key: path to the `value`.
            type_: expected type of `value`.
            default: default value to use.
            key_type: expected type of all keys of `value`,
                if `value` is a `dict`, and `key_type` is not `None`.
            value_type: expected type of all values of `value`,
                if `value` is a `dict` or `list`, and `value_type` is not `None`.

        Returns:
            `value` at `key`: if `value` found.
            `default`: if `value` not found.
            `type()`: if `value` not found and no `default` provided.

        """
        try:
            value = self._get_item(key)
            return ensure_cast(
                value, type_, default, key_type=key_type, value_type=value_type
            )

        except:  # noqa: E722
            return default or type_()

    @overload
    def expect[T](self, key: int | str, type_: type[T]) -> T: ...

    @overload
    def expect[V](
        self, key: int | str, type_: type[list], *, value_type: type[V]
    ) -> list[V]: ...

    @overload
    def expect[K, V](
        self,
        key: int | str,
        type_: type[dict],
        *,
        key_type: type[K],
        value_type: type[V],
    ) -> dict[K, V]: ...

    def expect[T, K, V](
        self,
        key: int | str,
        type_: type[T],
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> Any:
        """
        Expect the `value` to be present and of the specified `type`.

        Args:
            key: path to the `value`.
            type_: expected type of `value`.
            key_type: expected type of all keys of `value`,
                if `value` is a `dict`, and `key_type` is not `None`.
            value_type: expected type of all values of `value`,
                if `value` is a `dict` or `list`, and `value_type` is not `None`.

        Returns:
            `value` at path.

        Raises:
            `KeyError`: if `chaining` is enabled and the `key` cannot be found.
            `IndexError`: if `chaining` is enabled and the `index` is out of range.
            `TypeError`: if the `value` is not of the expected `type`.
            `TypeError`: if `chaining` is enabled and a `list` is indexed with a string.

        """
        val = self._get_item(key)
        return expect(val, type_, key_type=key_type, value_type=value_type)
