import pytest
from pfm_bottlenecks.bottleneck_definitions import (
    load_bottleneck_definition,
    get_schema,
    BOTTLENECK_SCHEMAS
)


class TestLoadBottleneckDefinition:
    """Tests for load_bottleneck_definition function."""

    def test_load_valid_bottleneck(self):
        """Test loading a valid bottleneck definition."""
        result = load_bottleneck_definition('1.1')

        assert result['id'] == '1.1'
        assert 'name' in result
        assert 'description' in result
        assert 'extended_definition' in result
        assert 'challenge_name' in result
        assert 'challenge_description' in result
        assert result['challenge_name'] == 'Insufficient Stakeholder Commitment to Policy Action'

    def test_load_bottleneck_with_extended_definition(self):
        """Test loading bottleneck with extended definition."""
        result = load_bottleneck_definition('2.1')

        assert result['id'] == '2.1'
        assert 'Malawi' in result['extended_definition']
        assert 'Kenya' in result['extended_definition']

    def test_load_bottleneck_without_extended_definition(self):
        """Test loading bottleneck without extended definition."""
        result = load_bottleneck_definition('1.1')

        assert result['extended_definition'] == ''

    def test_load_all_bottlenecks(self):
        """Test that all 31 bottlenecks can be loaded."""
        expected_ids = [
            '1.1', '1.2',
            '2.1', '2.2', '2.3',
            '3.1', '3.2', '3.3', '3.4', '3.5',
            '4.1', '4.2', '4.3', '4.4', '4.5',
            '5.1', '5.2', '5.3',
            '6.1', '6.2', '6.3', '6.4', '6.5', '6.6',
            '7.1', '7.2', '7.3', '7.4', '7.5',
            '8.1', '8.2'
        ]

        for bottleneck_id in expected_ids:
            result = load_bottleneck_definition(bottleneck_id)
            assert result['id'] == bottleneck_id

    def test_load_invalid_bottleneck(self):
        """Test loading a non-existent bottleneck."""
        with pytest.raises((ValueError, KeyError)):
            load_bottleneck_definition('99.9')

    def test_load_invalid_format(self):
        """Test loading with invalid ID format."""
        with pytest.raises((ValueError, KeyError)):
            load_bottleneck_definition('invalid')


class TestGetSchema:
    """Tests for get_schema function."""

    def test_get_schema_with_multiple_subschemas(self):
        """Test getting schema for bottleneck with multiple subschemas (1.1)."""
        schema = get_schema('1.1')

        assert isinstance(schema, list)
        assert len(schema) == 6

        # Check first subschema structure
        first_subschema = schema[0]
        assert 'subschema' in first_subschema
        assert 'strong_cues' in first_subschema
        assert 'moderate_cues' in first_subschema
        assert 'hard_negatives' in first_subschema
        assert 'failure_types' in first_subschema
        assert 'acceptance_rule' in first_subschema
        assert 'scope_lock' in first_subschema

    def test_get_schema_with_single_subschema(self):
        """Test getting schema for bottleneck with single subschema (2.1, 5.1)."""
        schema_2_1 = get_schema('2.1')
        assert isinstance(schema_2_1, list)
        assert len(schema_2_1) == 1

        schema_5_1 = get_schema('5.1')
        assert isinstance(schema_5_1, list)
        assert len(schema_5_1) == 1

    def test_get_schema_not_defined(self):
        """Test getting schema for bottleneck without schema defined."""
        with pytest.raises(ValueError, match="Bottleneck 2.2 not found"):
            get_schema('2.2')

    def test_get_schema_invalid_bottleneck(self):
        """Test getting schema for non-existent bottleneck."""
        with pytest.raises(ValueError, match="Bottleneck 99.9 not found"):
            get_schema('99.9')

    def test_available_schemas_count(self):
        """Test that correct number of schemas are available."""
        available = list(BOTTLENECK_SCHEMAS.keys())
        assert len(available) == 3
        assert set(available) == {'1.1', '2.1', '5.1'}

    def test_bottleneck_schemas_dict(self):
        """Test BOTTLENECK_SCHEMAS module constant."""
        assert isinstance(BOTTLENECK_SCHEMAS, dict)
        assert len(BOTTLENECK_SCHEMAS) == 3
        assert '1.1' in BOTTLENECK_SCHEMAS
        assert '2.1' in BOTTLENECK_SCHEMAS
        assert '5.1' in BOTTLENECK_SCHEMAS


class TestSchemaContent:
    """Tests for schema content validation."""

    def test_schema_1_1_subschemas(self):
        """Test 1.1 has expected subschemas."""
        schema = get_schema('1.1')
        subschema_names = [s['subschema'] for s in schema]

        expected_names = [
            'Reform Not Followed Through',
            'Political Resistance',
            'Interference in Execution',
            'Failure to Prioritize',
            'Passive Commitment Failure',
            'Delegated Leadership Failure'
        ]

        assert subschema_names == expected_names

    def test_schema_has_required_fields(self):
        """Test that all schemas have required fields."""
        for bottleneck_id in BOTTLENECK_SCHEMAS.keys():
            schema = get_schema(bottleneck_id)
            for subschema in schema:
                assert isinstance(subschema.get('strong_cues'), list)
                assert isinstance(subschema.get('moderate_cues'), list)
                assert isinstance(subschema.get('hard_negatives'), list)
                assert isinstance(subschema.get('failure_types'), list)
                assert isinstance(subschema.get('acceptance_rule'), str)

    def test_acceptance_rules_format(self):
        """Test that acceptance rules follow expected format."""
        for bottleneck_id in BOTTLENECK_SCHEMAS.keys():
            schema = get_schema(bottleneck_id)
            for subschema in schema:
                rule = subschema['acceptance_rule']
                # Should contain 'strong' and 'moderate' keywords
                assert 'strong' in rule.lower() or 'moderate' in rule.lower()
                # Should contain '>=' or '>'
                assert '>=' in rule or '>' in rule


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
