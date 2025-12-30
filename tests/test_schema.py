"""
Unit tests for the schema module.
"""

from src.schema import (
    SCHEMA,
    CertificationStandard,
    FieldDefinition,
    FieldType,
    GreenBondSchema,
    UseOfProceeds,
)


class TestFieldType:
    """Tests for FieldType enum."""

    def test_field_types_exist(self):
        """Test that all expected field types are defined."""
        assert FieldType.STRING is not None
        assert FieldType.FLOAT is not None
        assert FieldType.INTEGER is not None
        assert FieldType.DATE is not None
        assert FieldType.BOOLEAN is not None


class TestUseOfProceeds:
    """Tests for UseOfProceeds enum."""

    def test_has_renewable_energy(self):
        """Test that Renewable Energy category exists."""
        assert UseOfProceeds.RENEWABLE_ENERGY.value == "Renewable Energy"

    def test_values_method_returns_list(self):
        """Test that values() returns a list of strings."""
        values = UseOfProceeds.values()
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, str) for v in values)

    def test_all_categories_present(self):
        """Test that expected categories are present."""
        values = UseOfProceeds.values()
        assert "Renewable Energy" in values
        assert "Clean Transportation" in values
        assert "Green Buildings" in values


class TestCertificationStandard:
    """Tests for CertificationStandard enum."""

    def test_has_climate_bonds_initiative(self):
        """Test that Climate Bonds Initiative standard exists."""
        assert CertificationStandard.CLIMATE_BONDS_INITIATIVE.value == "Climate Bonds Initiative"

    def test_values_method_returns_list(self):
        """Test that values() returns a list of strings."""
        values = CertificationStandard.values()
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, str) for v in values)


class TestFieldDefinition:
    """Tests for FieldDefinition dataclass."""

    def test_create_simple_field(self):
        """Test creating a simple field definition."""
        field = FieldDefinition(name="test_field", type=FieldType.STRING, required=True)
        assert field.name == "test_field"
        assert field.type == FieldType.STRING
        assert field.required is True

    def test_create_field_with_constraints(self):
        """Test creating a field with validation constraints."""
        field = FieldDefinition(
            name="amount",
            type=FieldType.FLOAT,
            required=True,
            min_value=0.0,
            max_value=10000.0,
        )
        assert field.min_value == 0.0
        assert field.max_value == 10000.0

    def test_create_field_with_pattern(self):
        """Test creating a field with regex pattern."""
        field = FieldDefinition(
            name="code",
            type=FieldType.STRING,
            pattern=r"^[A-Z]{3}$",
        )
        assert field.pattern == r"^[A-Z]{3}$"


class TestGreenBondSchema:
    """Tests for GreenBondSchema class."""

    def test_schema_has_fields(self):
        """Test that schema initializes with fields."""
        schema = GreenBondSchema()
        assert len(schema.fields) > 0

    def test_schema_has_required_fields(self):
        """Test that schema has the expected required fields."""
        schema = GreenBondSchema()
        required_names = schema.get_required_field_names()

        assert "bond_id" in required_names
        assert "issuer" in required_names
        assert "country_code" in required_names
        assert "amount_usd_millions" in required_names

    def test_get_field_by_name(self):
        """Test retrieving a specific field by name."""
        schema = GreenBondSchema()
        field = schema.get_field("bond_id")

        assert field is not None
        assert field.name == "bond_id"
        assert field.required is True

    def test_get_nonexistent_field_returns_none(self):
        """Test that getting a nonexistent field returns None."""
        schema = GreenBondSchema()
        field = schema.get_field("nonexistent_field")
        assert field is None

    def test_get_required_fields(self):
        """Test getting list of required fields."""
        schema = GreenBondSchema()
        required = schema.get_required_fields()

        assert len(required) > 0
        assert all(f.required for f in required)

    def test_get_optional_fields(self):
        """Test getting list of optional fields."""
        schema = GreenBondSchema()
        optional = schema.get_optional_fields()

        assert len(optional) > 0
        assert all(not f.required for f in optional)

    def test_get_field_names(self):
        """Test getting list of all field names."""
        schema = GreenBondSchema()
        names = schema.get_field_names()

        assert isinstance(names, list)
        assert "bond_id" in names
        assert "amount_usd_millions" in names
        assert "use_of_proceeds" in names

    def test_country_code_field_constraints(self):
        """Test that country_code field has proper constraints."""
        schema = GreenBondSchema()
        field = schema.get_field("country_code")

        assert field is not None
        assert field.min_length == 3
        assert field.max_length == 3
        assert field.pattern is not None

    def test_amount_field_constraints(self):
        """Test that amount_usd_millions has proper constraints."""
        schema = GreenBondSchema()
        field = schema.get_field("amount_usd_millions")

        assert field is not None
        assert field.type == FieldType.FLOAT
        assert field.min_value == 0.0


class TestGlobalSchema:
    """Tests for the global SCHEMA instance."""

    def test_global_schema_exists(self):
        """Test that SCHEMA constant is defined."""
        assert SCHEMA is not None
        assert isinstance(SCHEMA, GreenBondSchema)

    def test_schema_version(self):
        """Test that schema has a version."""
        assert SCHEMA.version is not None
        assert isinstance(SCHEMA.version, str)
