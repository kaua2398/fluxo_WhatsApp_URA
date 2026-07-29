import json

import pytest

from app.parsers.blip_parser import BlipParser
from app.parsers.classifier import NodeClassifier
from app.parsers.ura_parser import UraParser


SAMPLE_BLIP = {
    "id": "root",
    "title": "Início",
    "type": "start",
    "states": [
        {
            "id": "menu_main",
            "title": "Menu Principal",
            "type": "menu",
            "transitions": {
                "1": "consultar_saldo",
                "2": "cartoes",
            },
        },
        {
            "id": "consultar_saldo",
            "title": "Consultar Saldo",
            "type": "message",
            "next": "api_saldo",
        },
        {
            "id": "api_saldo",
            "title": "API Consulta Saldo",
            "type": "http-request",
            "url": "https://api.example.com/saldo",
            "method": "GET",
            "success": "show_saldo",
            "failure": "error_handler",
        },
        {
            "id": "show_saldo",
            "title": "Exibir Saldo",
            "type": "message",
            "next": "end_flow",
        },
        {
            "id": "cartoes",
            "title": "Cartões",
            "type": "menu",
            "transitions": {"1": "segunda_via"},
        },
        {
            "id": "segunda_via",
            "title": "Segunda Via",
            "type": "message",
        },
        {
            "id": "error_handler",
            "title": "Erro no Sistema",
            "type": "error",
        },
        {
            "id": "end_flow",
            "title": "Finalizar",
            "type": "end",
        },
    ],
}


SAMPLE_URA_JSON = {
    "nodes": [
        {"id": "welcome", "label": "Bem-vindo", "type": "start", "next": "main_menu"},
        {
            "id": "main_menu",
            "label": "Menu Principal",
            "type": "menu",
            "transitions": {"1": "consulta", "2": "transfer_human"},
        },
        {"id": "consulta", "label": "Consulta de Saldo", "type": "message", "next": "end"},
        {"id": "transfer_human", "label": "Transferir para Atendente", "type": "human", "next": "end"},
        {"id": "end", "label": "Encerrar Chamada", "type": "end"},
    ]
}


class TestNodeClassifier:
    def test_classify_menu(self):
        assert NodeClassifier.classify("Menu Principal") == "menu"

    def test_classify_api(self):
        assert NodeClassifier.classify("HTTP Request API") == "api"

    def test_classify_condition(self):
        assert NodeClassifier.classify("Verificar condição") == "condition"

    def test_classify_human(self):
        assert NodeClassifier.classify("Transfer to human attendant") == "human_handoff"

    def test_classify_error(self):
        assert NodeClassifier.classify("Error handler timeout") == "error"


class TestBlipParser:
    def setup_method(self):
        self.parser = BlipParser()

    def test_can_parse_json(self):
        assert self.parser.can_parse("flow.json")

    def test_parse_creates_nodes(self):
        content = json.dumps(SAMPLE_BLIP)
        graph = self.parser.parse(content)
        assert len(graph.nodes) > 0

    def test_parse_creates_edges(self):
        content = json.dumps(SAMPLE_BLIP)
        graph = self.parser.parse(content)
        assert len(graph.edges) > 0

    def test_parse_detects_api(self):
        content = json.dumps(SAMPLE_BLIP)
        graph = self.parser.parse(content)
        assert len(graph.apis) > 0

    def test_parse_organizes_modules(self):
        content = json.dumps(SAMPLE_BLIP)
        graph = self.parser.parse(content)
        assert len(graph.modules) > 0
        for node in graph.nodes:
            assert node.module


class TestUraParser:
    def setup_method(self):
        self.parser = UraParser()

    def test_can_parse_json(self):
        assert self.parser.can_parse("ura.json")

    def test_can_parse_pdf(self):
        assert self.parser.can_parse("ura.pdf")

    def test_parse_json_creates_nodes(self):
        content = json.dumps(SAMPLE_URA_JSON)
        graph = self.parser.parse(content, metadata={"filename": "ura.json"})
        assert len(graph.nodes) >= 5

    def test_parse_json_creates_edges(self):
        content = json.dumps(SAMPLE_URA_JSON)
        graph = self.parser.parse(content, metadata={"filename": "ura.json"})
        assert len(graph.edges) > 0

    def test_parse_text_as_pdf_fallback(self):
        text = "Menu Principal\nOpção 1: Consultar Saldo → show_balance\nFinalizar chamada"
        graph = self.parser.parse(text.encode(), metadata={"filename": "ura.pdf"})
        assert len(graph.nodes) > 0
