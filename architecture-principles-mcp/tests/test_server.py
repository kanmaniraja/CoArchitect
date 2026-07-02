import pytest
from src.server import list_principles, get_principle, validate_code, get_principle_resource

def test_list_principles():
    principles = list_principles()
    assert isinstance(principles, list)
    assert len(principles) >= 2
    
    # Check that key entries exist
    names = [p["name"] for p in principles]
    assert "SingleResponsibility" in names
    assert "DependencyInversion" in names
    
    # Check shape
    for p in principles:
        assert "name" in p
        assert "uri" in p
        assert "summary" in p
        assert p["uri"].startswith("principles://")

def test_get_principle():
    markdown = get_principle("SingleResponsibility")
    assert isinstance(markdown, str)
    assert "Single Responsibility Principle" in markdown
    assert "❌ Violation Example" in markdown

def test_get_principle_case_insensitive_and_spacing():
    markdown = get_principle("  dependencyinversion  ")
    assert isinstance(markdown, str)
    assert "Dependency Inversion Principle" in markdown

def test_get_principle_not_found():
    with pytest.raises(ValueError) as exc_info:
        get_principle("NonExistentPrinciple")
    assert "Principle 'NonExistentPrinciple' not found" in str(exc_info.value)

def test_get_principle_resource():
    markdown = get_principle_resource("SingleResponsibility")
    assert isinstance(markdown, str)
    assert "Single Responsibility Principle" in markdown

def test_validate_code_tool_conforming():
    code = """
class DataModel:
    def __init__(self, value: int):
        self.value = value
"""
    report_md = validate_code(code, principle="srp")
    assert "✅ CONFORMING" in report_md
    assert "Quality Score" in report_md

def test_validate_code_tool_violating():
    code = """
class NotificationManager:
    def __init__(self):
        self.sender = SMTPClient()
"""
    report_md = validate_code(code, principle="all")
    assert "❌ NON-CONFORMING" in report_md
    assert "DIP_Hardcoded_Dependency" in report_md
    assert "SRP_Naming_AntiPattern" in report_md
