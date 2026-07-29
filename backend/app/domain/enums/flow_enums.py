from enum import StrEnum


class FlowType(StrEnum):
    WHATSAPP = "whatsapp"
    URA = "ura"
    COMMERCIAL = "commercial"
    EMAIL = "email"
    GENERIC = "generic"


class NodeType(StrEnum):
    START = "start"
    END = "end"
    MENU = "menu"
    SUBMENU = "submenu"
    MESSAGE = "message"
    CONDITION = "condition"
    API = "api"
    VARIABLE = "variable"
    HUMAN_HANDOFF = "human_handoff"
    ERROR = "error"
    FLOW = "flow"
    MODULE = "module"
    UNKNOWN = "unknown"


class EdgeType(StrEnum):
    DEFAULT = "default"
    CONDITION_TRUE = "condition_true"
    CONDITION_FALSE = "condition_false"
    ERROR = "error"
    TIMEOUT = "timeout"
    MENU_OPTION = "menu_option"


class ExportFormat(StrEnum):
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class FileSourceType(StrEnum):
    BLIP_JSON = "blip_json"
    URA_PDF = "ura_pdf"
    URA_JSON = "ura_json"
    GENERIC_JSON = "generic_json"
