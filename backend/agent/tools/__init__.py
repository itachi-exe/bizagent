"""Safe, database-backed actions exposed to the BizAgent model."""

from .calculate_price import calculate_price
from .check_inventory import check_inventory
from .create_order import create_order
from .create_quote import create_quote
from .escalate_to_human import escalate_to_human
from .search_product import search_product

TOOL_HANDLERS = {
    "search_product": search_product,
    "check_inventory": check_inventory,
    "calculate_price": calculate_price,
    "create_quote": create_quote,
    "create_order": create_order,
    "escalate_to_human": escalate_to_human,
}
