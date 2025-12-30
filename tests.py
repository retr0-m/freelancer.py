from lead import Lead
def test_from_lead_realistic():
    """
    Uses realistic data so Lead(), LocaleInfo, and config dependencies work.
    """

    lead = Lead(
        id=42,
        name="Bäckerei Steiner",
        phone="+41445556677",
        email="info@baeckerei-steiner.ch",
        address="Bahnhofstrasse 12, 8001 Zürich, Switzerland",
        city="Zürich",
        images=[],
        status=0
    )

    # result = from_lead(lead)

    # assert result is None or isinstance(result, dict), "Invalid return type"

    # if result:
    #     assert "handle" in result
    #     assert "url" in result
    #     assert "confidence" in result
    #     assert result["url"].startswith("https://instagram.com/")

    # print("✅ test_from_lead_realistic passed")
    # print("Result:", result)

    print(lead.fetch_instagram())

test_from_lead_realistic()