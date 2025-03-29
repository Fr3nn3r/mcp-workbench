import pytest
from mcp.spec_registry import SUPPORTED_SPECS


@pytest.mark.mcp_requirement(feature="spec/version", level="MUST")
def test_spec_version_is_supported(spec_version):
    """Test that the spec version is registered and supported."""
    assert (
        spec_version in SUPPORTED_SPECS
    ), f"Spec version {spec_version} is not supported"


@pytest.mark.mcp_requirement(feature="spec/features", level="MUST")
def test_spec_features_are_defined(spec_version):
    """Test that the spec version has defined features."""
    features = SUPPORTED_SPECS[spec_version]["features"]
    assert isinstance(features, list), "Features should be defined as a list"
    assert len(features) > 0, "Spec version should have at least one feature"
