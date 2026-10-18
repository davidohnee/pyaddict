"""OneOf schema definition."""

from typing import Any

from pyaddict.schema.base import ISchemaType, Validatable
from pyaddict.schema.common import format_repr, validate
from pyaddict.schema.result import ValidationError, ValidationResult


class OneOf(ISchemaType["OneOf", Any | None]):
    """The value must match any of the provided schemas."""

    def __init__(self, *schemas: Validatable) -> None:
        """Create a OneOf schema definition."""
        super().__init__()
        self._schemas = list(schemas)

    def nullable(self) -> Any:
        """
        Allow the property to be None/null.

        Use `.default()` to set a default value for the result.

        Returns:
            self.

        """
        return self

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[Any | None]:
        """
        Validate the provided value.

        Returns:
            ValidationResult.

        """
        path = path or []
        errors: list[ValidationError] = []

        for schema in self._schemas:
            result = validate(value, schema, path=path)
            if result:
                return result
            if not result and result.error:
                errors.append(result.error)

        return ValidationResult.err(
            ValidationError(
                "value didn't match any of the schemas", path, "one_of", cause=errors
            )
        )

    def __repr__(self) -> str:
        """Representation."""
        fields: list[str] = []
        fields.append("\n| ".join([repr(x) for x in self._schemas]))
        if self._nullable:
            fields.append("nullable")
        return "OneOf(" + format_repr(fields) + ")"
