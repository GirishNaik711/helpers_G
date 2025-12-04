TigerGraph” with minimal friction.
There are two issues and the cleanest fixes:
1️⃣ Vertex error: "Content" is not a valid vertex type
Best solution:
👉 Make schema match your JSON. Add Content as a vertex instead of hacking the loader.
GSQL changes (edit create_schema.gsql)
Add before CREATE GRAPH FinancialAdvisor:
Copy code
Sql
CREATE VERTEX Content (
  PRIMARY_ID id STRING,
  title STRING,
  body STRING,
  meta STRING,
  embedding LIST<DOUBLE>
) WITH PRIMARY_ID_AS_ATTRIBUTE="true";
Then update the graph definition to include it:
Copy code
Sql
CREATE GRAPH FinancialAdvisor (
  Advisor,
  Client,
  Assets,
  Content,
  ADVISES,
  INVESTS_IN
);
For dev/demo, easiest is:
Copy code
Sql
DROP GRAPH FinancialAdvisor
@create_schema.gsql   -- or paste & run your whole schema script again
Now TigerGraph accepts vertex type Content from your JSON.
2️⃣ Edge error: string indices must be integers, not 'str'
Your all_edges.json is a dict-of-lists, not a flat list.
We fix this by flattening it before looping.
✅ Final, “optimum” JSON loaders
Use these two functions (you can keep everything else as-is):
Copy code
Python
import json, os
DATA_DIR = "data"

# ---------- helper to infer primary id ----------
def _infer_primary_id(v: dict):
    # Use explicit _id if present
    if "_id" in v:
        return v["_id"]

    attrs = v.get("attributes", {}) or {}

    # Try common id patterns
    for k in attrs.keys():
        if k.endswith("_id") or k == "id":
            return attrs[k]

    raise KeyError(f"Could not infer primary id for vertex: {v}")


# ---------- vertices ----------
def load_vertices_json(path=os.path.join(DATA_DIR, "all_vertices.json")):
    """
    Supports:
      { "Advisor": [ {...}, ... ], "Client": [ {...}, ... ] }
      or [ {...}, {...}, ... ]
    """
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


# ---------- edges ----------
def load_edges_json(path=os.path.join(DATA_DIR, "all_edges.json")):
    """
    Supports:
      { "ADVISES": [ {...}, ... ], "INVESTS_IN": [ {...}, ... ] }
      or [ {...}, {...}, ... ]
    """
    logger.info(f"Loading edges from JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    edges = []
    if isinstance(data, dict):
        for edge_type, lst in data.items():
            if not isinstance(lst, list):
                continue
            for obj in lst:
                obj.setdefault("e_type", edge_type)
                edges.append(obj)
    elif isinstance(data, list):
        edges = data
    else:
        logger.error("Unexpected edges JSON format")
        return

    total = len(edges)
    logger.info(f"Found {total} edges")

    for idx, e in enumerate(edges, start=1):
        upsert_edge(
            e["from_type"],
            e["from_id"],
            e["to_type"],
            e["to_id"],
            e["e_type"],
            e.get("attributes", {}) or {},
        )

        if idx % 50 == 0 or idx == total:
            logger.debug(f"Loaded {idx}/{total} edges")

    logger.success("Completed loading edges from JSON")
After this:
Update schema to include Content (and any other new vertex types like WebPage if you use them).
Rerun schema in GSQL.
Run Python:
Copy code
Python
load_vertices_json()
load_edges_json()
