"""OpenAI function schemas. Keep these aligned with the typed tool functions."""

def _tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {"type": "function", "function": {"name": name, "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required,
                           "additionalProperties": False}}}


TOOL_SCHEMAS = [
    _tool("search_product", "Search products. Always use before quoting any price.",
          {"query": {"type": "string", "description": "Product name or search term."}}, ["query"]),
    _tool("check_inventory", "Check current stock for a product returned by search_product.",
          {"product_id": {"type": "string", "description": "Product UUID."}}, ["product_id"]),
    _tool("calculate_price", "Calculate product total. Only pass a discount if explicitly requested.",
          {"product_id": {"type": "string"}, "quantity": {"type": "integer", "minimum": 1},
           "discount_pct": {"type": "integer", "minimum": 0, "default": 0}}, ["product_id", "quantity"]),
    _tool("create_quote", "Create a formal quote after the customer asks for one.",
          {"line_items": {"type": "array", "minItems": 1, "items": {"type": "object", "properties":
              {"product_id": {"type": "string"}, "quantity": {"type": "integer", "minimum": 1}},
              "required": ["product_id", "quantity"], "additionalProperties": False}},
           "discount_pct": {"type": "integer", "minimum": 0, "default": 0}}, ["line_items"]),
    _tool("create_order", "Create a confirmed order only after explicit customer confirmation.",
          {"line_items": {"type": "array", "minItems": 1, "items": {"type": "object", "properties":
              {"product_id": {"type": "string"}, "quantity": {"type": "integer", "minimum": 1}},
              "required": ["product_id", "quantity"], "additionalProperties": False}},
           "discount_pct": {"type": "integer", "minimum": 0, "default": 0}, "notes": {"type": "string"}}, ["line_items"]),
    _tool("escalate_to_human", "Flag a request needing a team member.",
          {"reason": {"type": "string", "enum": ["discount_above_ceiling", "refund_request", "complaint", "out_of_scope", "customer_request"]},
           "summary": {"type": "string"}}, ["reason", "summary"]),
]
