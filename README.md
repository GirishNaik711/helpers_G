def _infer_primary_id(v: dict):
    # If _id exists, use it
    if "_id" in v:
        return v["_id"]

    attrs = v.get("attributes", {}) or {}
    # Try common id attribute names
    for k in ("advisor_id", "client_id", "Assets_id", "asset_id", "company_id", "id"):
        if k in attrs:
            return attrs[k]

    raise KeyError("_id")  # fallback – will show which object is bad


def load_vertices_json(path=os.path.join(DATA_DIR, "all_vertices.json")):
    """Load vertices from JSON (supports dict-of-lists and list)."""
    logger.info(f"Loading vertices from JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = []
    if isinstance(data, dict):
        for v_type, verts in data.items():
            if not isinstance(verts, list):
                continue
            for obj in verts:
                obj.setdefault("_type", v_type)
                items.append(obj)
    elif isinstance(data, list):
        items = data
    else:
        logger.error("Unexpected JSON format for vertices")
        return

    total = len(items)
    logger.info(f"Found {total} vertices")

    for idx, v in enumerate(items, start=1):
        v_type = v["_type"]
        v_id = _infer_primary_id(v)
        attrs = v.get("attributes", {}) or {}

        upsert_vertex(v_type, v_id, attrs)

        if idx % 100 == 0 or idx == total:
            logger.debug(f"Loaded {idx}/{total} vertices")

    logger.success("Completed loading vertices from JSON")
