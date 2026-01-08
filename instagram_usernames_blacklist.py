BLACKLIST_KEYWORDS = {
    "explore", "hub", "daily", "official", "media", "news",
    "repost", "feature", "submit", "promo", "giveaway",
    "crypto", "nft", "forex", "casino",
    "shop", "store", "brand", "agency", "studio",
    "team", "admin", "press"
}

RESERVED_USERNAMES = {
    "explore", "help", "support", "about", "privacy", "terms",
    "ads", "business", "developers", "instagram", "meta"
}

def is_blacklisted(username: str) -> bool:
    u = username.lower()

    if u in RESERVED_USERNAMES:
        return True

    if any(k in u for k in BLACKLIST_KEYWORDS):
        return True

    if sum(c.isdigit() for c in u) > 4:
        return True

    if u.endswith(tuple("0123456789")) and u[-2:].isdigit():
        return True

    if "__" in u:
        return True

    if len(u) < 4:
        return True

    return False