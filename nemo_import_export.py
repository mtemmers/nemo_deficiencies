"""
Export NEMO report definitions from a project.

Default behavior:
  - reads all reports from the NEMO project "Master Data"
  - writes one SQL file per report
  - writes a JSON metadata dump
  - writes a CSV index

Optional:
  - with --export-data, executes every report and writes the result as CSV
  - with --report/--contains, limits the export to selected reports
  - with --refresh-index, regenerates the full report catalog on demand
  - with --showreports, prints the available reports and exits
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Tuple

from backend.services.config_discovery import resolve_config_path
from backend.services.nemo_client import create_nemo_client, get_reports
from backend.services.report_service import export_report_data
from backend.services.report_utils import (
    read_report_file,
    select_reports,
    write_index_csv,
    write_json,
    write_report_sql_files,
)

DEFAULT_PROJECT = "Master Data"
DEFAULT_OUTPUT_DIR = Path("exports") / "master_data_reports"

log = logging.getLogger("nemo_import_export")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Liest alle NEMO Reports aus einem Projekt und exportiert sie lokal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python nemo_import_export.py
  python nemo_import_export.py -c config_gmt.ini
  python nemo_import_export.py -p "Master Data" -o ./exports/master_data
  python nemo_import_export.py --export-data
  python nemo_import_export.py -r "(DEFICIENCIES) Addresses" --data-output ./exports/selected
  python nemo_import_export.py --contains paDQM --data-output ./exports/padqm
  python nemo_import_export.py --refresh-index
  python nemo_import_export.py --showreports
        """,
    )
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Dateiname aus config/ oder Pfad zur NEMO config.ini. Ohne Angabe wird in config/ gesucht.",
    )
    parser.add_argument(
        "-p",
        "--project",
        default=DEFAULT_PROJECT,
        help='NEMO Projektname. Default: "Master Data".',
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Ausgabeverzeichnis. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--filter",
        default="*",
        help='Optionaler Report-Filter fuer nemo_library.getReports(). Default: "*".',
    )
    parser.add_argument(
        "-r",
        "--report",
        action="append",
        default=[],
        help="Ausgewaehlter Report per displayName, internalName oder id. Kann mehrfach verwendet werden.",
    )
    parser.add_argument(
        "--contains",
        action="append",
        default=[],
        help="Waehlt Reports, deren displayName oder internalName diesen Text enthaelt. Kann mehrfach verwendet werden.",
    )
    parser.add_argument(
        "--report-file",
        default=None,
        help="Textdatei mit auszuwaehlenden Reports, ein displayName/internalName/id pro Zeile.",
    )
    parser.add_argument(
        "--refresh-index",
        action="store_true",
        help="Gesamtindex und Metadata-Datei neu erzeugen, auch bei einer Report-Auswahl.",
    )
    parser.add_argument(
        "--showreports",
        "--show-reports",
        action="store_true",
        help="Verfuegbare Reports als Liste ausgeben und beenden.",
    )
    parser.add_argument(
        "--no-sql",
        action="store_true",
        help="Keine einzelnen SQL-Dateien schreiben.",
    )
    parser.add_argument(
        "--export-data",
        action="store_true",
        help="Reports zusaetzlich ausfuehren und die Ergebnisse als CSV exportieren.",
    )
    parser.add_argument(
        "--data-output",
        default=None,
        help="Zielordner fuer die CSV-Ausgabe ausgefuehrter Reports. Aktiviert automatisch --export-data.",
    )
    parser.add_argument(
        "--separator",
        default=";",
        help='CSV-Trennzeichen fuer --export-data und den Index. Default: ";".',
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help='Datei-Encoding fuer CSV/SQL-Ausgaben. Default: "utf-8-sig".',
    )
    parser.add_argument(
        "--max-reports",
        type=int,
        default=None,
        help="Optional nur die ersten N Reports verarbeiten, hilfreich zum Testen.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mehr Log-Ausgaben anzeigen.",
    )
    return parser.parse_args()


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)

    if args.data_output:
        args.export_data = True

    config_path = resolve_config_path(args.config)
    if not config_path:
        log.error("Keine *.ini Config-Datei im Hauptordner oder darunter gefunden.")
        return 2
    if not config_path.exists():
        log.error("Config-Datei nicht gefunden: %s", config_path)
        return 2
    if not args.config:
        log.info("Automatisch gefundene Config: %s", config_path)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    log.info("Verbinde mit NEMO ueber Config: %s", config_path)
    nemo = create_nemo_client(config_path)

    log.info("Lese Reports aus Projekt '%s'...", args.project)
    all_reports = get_reports(nemo=nemo, project=args.project, filter_value=args.filter)

    if not all_reports:
        log.warning("Keine Reports gefunden.")
        return 0

    if args.showreports:
        for index, report in enumerate(all_reports, start=1):
            display_name = report.get("displayName") or ""
            internal_name = report.get("internalName") or ""
            print(f"{index:03d};{display_name};{internal_name}")
        return 0

    report_selection = list(args.report)
    selection_requested = bool(report_selection or args.contains or args.report_file)
    if args.report_file:
        report_file = Path(args.report_file)
        if not report_file.exists():
            log.error("Report-Auswahldatei nicht gefunden: %s", report_file)
            return 2
        report_selection.extend(read_report_file(report_file))

    reports = select_reports(
        reports=all_reports,
        exact_values=report_selection,
        contains_values=args.contains,
    )

    if args.max_reports is not None:
        reports = reports[: args.max_reports]

    if not reports:
        log.warning("Keine passenden Reports gefunden.")
        return 0

    log.info("%d Reports gefunden.", len(reports))

    metadata_path = output_dir / "reports_metadata.json"
    index_path = output_dir / "reports_index.csv"
    should_write_catalog = args.refresh_index or not selection_requested
    catalog_reports = all_reports if args.refresh_index and selection_requested else reports

    sql_files: Dict[int, str] = {}
    if not args.no_sql:
        sql_reports = catalog_reports if should_write_catalog else reports
        sql_files = write_report_sql_files(
            reports=sql_reports,
            sql_dir=output_dir / "sql",
            encoding=args.encoding,
        )
        log.info("%d SQL-Dateien geschrieben.", len(sql_files))

    data_files: Dict[int, str] = {}
    data_shapes: Dict[int, Tuple[int, int]] = {}
    data_errors: Dict[int, str] = {}
    if args.export_data:
        data_dir = Path(args.data_output) if args.data_output else output_dir / "data"
        data_files, data_shapes, data_errors = export_report_data(
            nemo=nemo,
            project=args.project,
            reports=reports,
            data_dir=data_dir,
            separator=args.separator,
            encoding=args.encoding,
        )

    if should_write_catalog:
        catalog_matches_export_selection = catalog_reports is reports
        write_json(metadata_path, catalog_reports)
        write_index_csv(
            path=index_path,
            reports=catalog_reports,
            sql_files=sql_files,
            data_files=data_files if catalog_matches_export_selection else {},
            data_shapes=data_shapes if catalog_matches_export_selection else {},
            data_errors=data_errors if catalog_matches_export_selection else {},
            separator=args.separator,
            encoding=args.encoding,
        )
    else:
        log.info("Index bleibt unveraendert: %s", index_path)

    log.info("Fertig.")
    if should_write_catalog:
        log.info("Metadata: %s", metadata_path)
        log.info("Index:    %s", index_path)
    if sql_files:
        log.info("SQL:      %s", output_dir / "sql")
    if args.export_data:
        log.info("Daten:    %s", Path(args.data_output) if args.data_output else output_dir / "data")
        if data_errors:
            log.warning("%d Reportdaten-Exports sind fehlgeschlagen. Details stehen im Index.", len(data_errors))

    return 1 if data_errors else 0


if __name__ == "__main__":
    sys.exit(main())
