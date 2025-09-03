def validate(location_text: str) -> bool:
    """
    Simple heuristic for civic/open spaces.
    Replace with GIS lookup later.
    """
    if not location_text:
        return False
    keywords = [
        "park", "reserve", "oval", "foreshore", "beach", "hall",
        "community centre", "plaza", "square", "public", "green"
    ]
    l = location_text.lower()
    return any(k in l for k in keywords)
