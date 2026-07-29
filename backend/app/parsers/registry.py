from typing import Any

from app.domain.enums.flow_enums import FileSourceType
from app.parsers.base import BaseParser
from app.parsers.blip_parser import BlipParser
from app.parsers.ura_parser import UraParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: list[BaseParser] = [BlipParser(), UraParser()]

    def get_parser(self, filename: str, content_type: str | None = None, flow_type: str | None = None) -> BaseParser:
        if flow_type == "whatsapp":
            return BlipParser()
        if flow_type == "ura":
            return UraParser()

        for parser in self._parsers:
            if parser.can_parse(filename, content_type):
                return parser

        if filename.lower().endswith(".json"):
            return BlipParser()
        if filename.lower().endswith(".pdf"):
            return UraParser()

        raise ValueError(f"No parser available for file: {filename}")

    def detect_source_type(self, filename: str, flow_type: str | None = None) -> str:
        lower = filename.lower()
        if flow_type == "whatsapp" or (lower.endswith(".json") and flow_type != "ura"):
            return FileSourceType.BLIP_JSON.value
        if lower.endswith(".pdf"):
            return FileSourceType.URA_PDF.value
        if lower.endswith(".json"):
            return FileSourceType.URA_JSON.value
        return FileSourceType.GENERIC_JSON.value


parser_registry = ParserRegistry()
