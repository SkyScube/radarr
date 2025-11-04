#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from classe import ssh
from index import commande


class ReportConfig:
    """Configuration des rapports disponibles."""

    def __init__(self):
        self._reports: Dict[str, Dict[str, str]] = {
            "users": {
                "method": "user_domain",
                "title": "Utilisateurs du domaine",
            },
            "groups": {
                "method": "group_user_domain",
                "title": "Groupes Active Directory",
            },
            "computers": {
                "method": "computers_domain",
                "title": "Machines du domaine",
            },
            "domain_controllers": {
                "method": "domain_controllers",
                "title": "Contrôleurs de domaine",
            },
        }
        self._alias_flags = ("users", "groups", "computers", "domain_controllers")

    def get_report_metadata(self, report_name: str) -> Dict[str, str]:
        """Retourne les métadonnées d'un rapport."""
        return self._reports[report_name]

    def get_all_report_names(self) -> List[str]:
        """Retourne la liste de tous les noms de rapports."""
        return list(self._reports.keys())

    def get_alias_flags(self) -> tuple:
        """Retourne les flags d'alias disponibles."""
        return self._alias_flags


class CLIArgumentParser:
    """Gestion des arguments de ligne de commande."""

    def __init__(self, config: ReportConfig):
        self.config = config

    def parse(self) -> argparse.Namespace:
        """Parse les arguments CLI et retourne le namespace."""
        parser = argparse.ArgumentParser(
            description="Collecte plusieurs rapports Active Directory et fusionne les résultats dans un fichier JSON."
        )
        parser.add_argument(
            "--users",
            action="store_true",
            help="Inclut le rapport utilisateurs (alias).",
        )
        parser.add_argument(
            "--groups",
            action="store_true",
            help="Inclut le rapport groupes (alias).",
        )
        parser.add_argument(
            "--computers",
            action="store_true",
            help="Inclut le rapport machines (alias).",
        )
        parser.add_argument(
            "--domain-controllers",
            dest="domain_controllers",
            action="store_true",
            help="Inclut le rapport contrôleurs de domaine (alias).",
        )
        parser.add_argument(
            "--name",
            required=True,
            help="Nom du fichier JSON généré (obligatoire).",
        )

        args = parser.parse_args()
        args.reports = self._resolve_reports(args)
        return args

    def _resolve_reports(self, args: argparse.Namespace) -> List[str]:
        """Détermine la liste finale des rapports à exécuter."""
        selected: List[str] = []
        for flag in self.config.get_alias_flags():
            if getattr(args, flag, False):
                selected.append(flag)
        if not selected:
            selected = self.config.get_all_report_names()
        return self._unique_preserve_order(selected)

    @staticmethod
    def _unique_preserve_order(values: List[str]) -> List[str]:
        """Élimine les doublons tout en préservant l'ordre."""
        seen: Dict[str, None] = {}
        ordered: List[str] = []
        for value in values:
            key = value.lower()
            if key not in seen:
                seen[key] = None
                ordered.append(value)
        return ordered


class ADReportCollector:
    """Collecte les rapports Active Directory via SSH."""

    def __init__(self, config: ReportConfig, host: str, username: str, password: str):
        self.config = config
        self.host = host
        self.username = username
        self.password = password
        self.client = ssh(host, username, password)
        self.exporter = commande()

    def collect(self, reports: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Ouvre une session SSH, exécute les rapports demandés et retourne les données."""
        self.client.connect()
        results: Dict[str, List[Dict[str, Any]]] = {}
        try:
            for report_name in reports:
                method_name = self.config.get_report_metadata(report_name)["method"]
                method = getattr(self.exporter, method_name)
                data = method(self.client)
                results[report_name] = [dict(record) for record in data]
        finally:
            self.client.close_connection()
        return results


class JSONDocumentBuilder:
    """Construction et sauvegarde de documents JSON."""

    def __init__(self, config: ReportConfig):
        self.config = config

    def build(self, host: str, order: List[str], payload: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Assemble un dictionnaire prêt à être converti en JSON."""
        sections: List[Dict[str, Any]] = []
        for report_name in order:
            meta = self.config.get_report_metadata(report_name)
            sections.append(
                {
                    "rapport": report_name,
                    "titre": meta["title"],
                    "donnees": payload.get(report_name, []),
                }
            )
        return {
            "serveur": host,
            "rapports": sections,
        }

    def save(self, document: Dict[str, Any], output_path: Path, filename: str) -> Path:
        """Sauvegarde le document JSON dans un fichier."""
        output_path.mkdir(parents=True, exist_ok=True)
        target = output_path / f"{filename}.json"
        with target.open("w", encoding="utf-8") as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
        return target


class ADReportExporter:
    """Orchestrateur principal pour l'exportation de rapports AD."""

    DEFAULT_HOST = "192.168.151.39"
    DEFAULT_USERNAME = "Administrateur"
    DEFAULT_PASSWORD = "AdminP4ss"
    DEFAULT_OUTPUT_PATH = Path.cwd()

    def __init__(
        self,
        host: str = None,
        username: str = None,
        password: str = None,
        output_path: Path = None,
    ):
        self.host = host or self.DEFAULT_HOST
        self.username = username or self.DEFAULT_USERNAME
        self.password = password or self.DEFAULT_PASSWORD
        self.output_path = output_path or self.DEFAULT_OUTPUT_PATH
        self.config = ReportConfig()

    def run(self) -> None:
        """Point d'entrée principal pour l'exécution."""
        parser = CLIArgumentParser(self.config)
        args = parser.parse()

        collector = ADReportCollector(self.config, self.host, self.username, self.password)
        payload = collector.collect(args.reports)

        builder = JSONDocumentBuilder(self.config)
        document = builder.build(self.host, args.reports, payload)
        target = builder.save(document, self.output_path, args.name)

        print(f"[enregistré] json -> {target}")


def main() -> None:
    """Point d'entrée du programme."""
    exporter = ADReportExporter()
    exporter.run()


if __name__ == "__main__":
    main()
