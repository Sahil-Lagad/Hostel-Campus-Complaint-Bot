from complaint_service import _fallback_classify

def test_water_category():
    result = _fallback_classify("Water is leaking from the tap")
    assert result["category"] == "Water"

def test_critical_fire():
    result = _fallback_classify("There is fire and smoke in the corridor")
    assert result["urgency"] == "Critical"

def test_default_other():
    result = _fallback_classify("I have a question about campus")
    assert result["category"] == "Other"
