"""
Green Bond Tracker - Schema Definition Module

This module serves as the single source of truth for the green bonds data schema.
It defines field names, types, validation rules, and allowed values.

Note: This is an educational project and should not be used for investment advice.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(Enum):
    """Data types for schema fields."""

    STRING = "string"
    FLOAT = "float"
    INTEGER = "integer"
    DATE = "date"
    BOOLEAN = "boolean"


class UseOfProceeds(Enum):
    """Recognized green project categories for bond proceeds."""

    RENEWABLE_ENERGY = "Renewable Energy"
    ENERGY_EFFICIENCY = "Energy Efficiency"
    CLEAN_TRANSPORTATION = "Clean Transportation"
    SUSTAINABLE_WATER = "Sustainable Water Management"
    POLLUTION_PREVENTION = "Pollution Prevention and Control"
    SUSTAINABLE_AGRICULTURE = "Sustainable Agriculture"
    GREEN_BUILDINGS = "Green Buildings"
    CLIMATE_ADAPTATION = "Climate Adaptation"
    BIODIVERSITY = "Biodiversity Conservation"

    @classmethod
    def values(cls) -> list[str]:
        """Return list of all category values."""
        return [e.value for e in cls]


class CertificationStandard(Enum):
    """Recognized green bond certification standards."""

    GREEN_BOND_PRINCIPLES = "Green Bond Principles"
    CLIMATE_BONDS_INITIATIVE = "Climate Bonds Initiative"
    EU_GREEN_BOND = "EU Green Bond Standard"
    ASEAN_GREEN_BOND = "ASEAN Green Bond Standards"
    CHINA_GREEN_BOND = "China Green Bond Guidelines"

    @classmethod
    def values(cls) -> list[str]:
        """Return list of all standard values."""
        return [e.value for e in cls]


@dataclass
class FieldDefinition:
    """Definition of a single field in the schema."""

    name: str
    type: FieldType
    required: bool = True
    description: str = ""
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    allowed_values: list[str] | None = None
    pattern: str | None = None
    example: Any | None = None

    def __post_init__(self):
        """Validate field definition after initialization."""
        if self.allowed_values is not None and not isinstance(self.allowed_values, list):
            self.allowed_values = list(self.allowed_values)


@dataclass
class GreenBondSchema:
    """Complete schema definition for green bonds data."""

    version: str = "1.0"
    fields: list[FieldDefinition] = field(default_factory=list)

    def __post_init__(self):
        """Initialize schema fields."""
        if not self.fields:
            self.fields = self._create_default_fields()

    @staticmethod
    def _create_default_fields() -> list[FieldDefinition]:
        """Create the default schema fields."""
        return [
            # Required fields
            FieldDefinition(
                name="bond_id",
                type=FieldType.STRING,
                required=True,
                description="Unique identifier for each bond",
                min_length=1,
                example="GB001",
            ),
            FieldDefinition(
                name="issuer",
                type=FieldType.STRING,
                required=True,
                description="Name of the organization issuing the bond",
                min_length=1,
                example="European Investment Bank",
            ),
            FieldDefinition(
                name="country_code",
                type=FieldType.STRING,
                required=True,
                description="ISO 3166-1 alpha-3 country code",
                min_length=3,
                max_length=3,
                pattern=r"^[A-Z]{3}$",
                example="USA",
            ),
            FieldDefinition(
                name="amount_usd_millions",
                type=FieldType.FLOAT,
                required=True,
                description="Bond amount in millions of USD",
                min_value=0.0,
                example=500.0,
            ),
            # Optional fields
            FieldDefinition(
                name="issue_date",
                type=FieldType.DATE,
                required=False,
                description="Date when the bond was issued (YYYY-MM-DD)",
                example="2023-01-15",
            ),
            FieldDefinition(
                name="maturity_date",
                type=FieldType.DATE,
                required=False,
                description="Date when the bond matures (YYYY-MM-DD)",
                example="2033-01-15",
            ),
            FieldDefinition(
                name="currency",
                type=FieldType.STRING,
                required=False,
                description="Original currency denomination (ISO 4217 code)",
                min_length=3,
                max_length=3,
                pattern=r"^[A-Z]{3}$",
                example="EUR",
            ),
            FieldDefinition(
                name="coupon_rate",
                type=FieldType.FLOAT,
                required=False,
                description="Annual coupon rate as a percentage",
                min_value=0.0,
                max_value=100.0,
                example=2.5,
            ),
            FieldDefinition(
                name="use_of_proceeds",
                type=FieldType.STRING,
                required=False,
                description="Category of green project funded by the bond",
                allowed_values=UseOfProceeds.values(),
                example="Renewable Energy",
            ),
            FieldDefinition(
                name="certification",
                type=FieldType.STRING,
                required=False,
                description="Green bond certification standard or framework",
                allowed_values=CertificationStandard.values(),
                example="Climate Bonds Initiative",
            ),
        ]

    def get_field(self, name: str) -> FieldDefinition | None:
        """Get a field definition by name."""
        for field_def in self.fields:
            if field_def.name == name:
                return field_def
        return None

    def get_required_fields(self) -> list[FieldDefinition]:
        """Get list of required fields."""
        return [f for f in self.fields if f.required]

    def get_optional_fields(self) -> list[FieldDefinition]:
        """Get list of optional fields."""
        return [f for f in self.fields if not f.required]

    def get_field_names(self) -> list[str]:
        """Get list of all field names."""
        return [f.name for f in self.fields]

    def get_required_field_names(self) -> list[str]:
        """Get list of required field names."""
        return [f.name for f in self.fields if f.required]


# Global schema instance
SCHEMA = GreenBondSchema()

# Constants for easy access
REQUIRED_FIELDS = SCHEMA.get_required_field_names()
ALL_FIELDS = SCHEMA.get_field_names()
USE_OF_PROCEEDS_CATEGORIES = UseOfProceeds.values()
CERTIFICATION_STANDARDS = CertificationStandard.values()
