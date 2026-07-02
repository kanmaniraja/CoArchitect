import pytest
from validator import ArchitectureValidator

def test_srp_violation_naming():
    code = """
class DatabaseManager:
    def __init__(self):
        self.connected = False
    
    def connect(self):
        pass
"""
    report = ArchitectureValidator.validate(code, target_principle="srp")
    assert not report.is_conforming
    assert any(f.rule_name == "SRP_Naming_AntiPattern" for f in report.findings)
    assert report.score < 100

def test_srp_violation_too_many_methods():
    code = """
class UserProfile:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
"""
    report = ArchitectureValidator.validate(code, target_principle="srp")
    assert not report.is_conforming
    assert any(f.rule_name == "SRP_Too_Many_Methods" for f in report.findings)

def test_srp_conforming():
    code = """
class UserProfile:
    def __init__(self, name: str):
        self.name = name
    def get_display_name(self) -> str:
        return self.name
"""
    report = ArchitectureValidator.validate(code, target_principle="srp")
    assert report.is_conforming
    assert len(report.findings) == 0
    assert report.score == 100

def test_dip_violation():
    code = """
class NotificationManager:
    def __init__(self):
        # Direct hardcoded instantiation of concrete class
        self.sender = SMTPClient()
    
    def notify(self, msg):
        self.sender.send(msg)
"""
    report = ArchitectureValidator.validate(code, target_principle="dip")
    assert not report.is_conforming
    assert any(f.rule_name == "DIP_Hardcoded_Dependency" for f in report.findings)
    # Check that standard dict() or list() or Exception are not flagged
    assert not any("dict" in f.message for f in report.findings)

def test_dip_conforming():
    code = """
class NotificationManager:
    def __init__(self, sender):
        # Dependency Injection (Conforming)
        self.sender = sender
    
    def notify(self, msg):
        self.sender.send(msg)
"""
    report = ArchitectureValidator.validate(code, target_principle="dip")
    assert report.is_conforming
    assert len(report.findings) == 0

def test_syntax_error_handling():
    code = "class ImproperPython: def"
    report = ArchitectureValidator.validate(code)
    assert not report.is_conforming
    assert len(report.findings) == 1
    assert report.findings[0].rule_name == "SyntaxError"
