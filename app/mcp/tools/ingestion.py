import json
import logging

from mcp.types import Tool

from app.scripts.lotto_data import LottoData

logger = logging.getLogger(__name__)

TOOLS = [
    Tool(
        name="fetch_latest_data",
        description="Fetch and ingest the latest lottery draw data from the NY Open Data portal",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


def _handle_fetch_latest_data(arguments: dict):
    try:
        lotto_data = LottoData()
        lotto_data.process_remote_lotto()
        return json.dumps({"status": "success", "message": "Data ingestion completed successfully"})
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        return json.dumps({"status": "error", "message": str(e)})


HANDLERS = {
    "fetch_latest_data": _handle_fetch_latest_data,
}
