from core.guardrails import check_non_prescriptive


def test_non_prescriptive_ok():
    text = "Rates can affect bond prices and equity valuations."
    res = check_non_prescriptive(text)
    assert res.ok is True


def test_non_prescriptive_blocks_advice():
    text = "You should buy AAPL now."
    res = check_non_prescriptive(text)
    assert res.ok is False
    assert "Prescriptive" in res.reasons[0]
