#!/usr/bin/env python3
"""Add default outcome columns based on the documented CREDENCE decisions."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


STATUS_PAID = {
    "Fully Paid",
    "Does not meet the credit policy. Status:Fully Paid",
}

STATUS_DEFAULT = {
    "Charged Off",
    "Default",
    "Does not meet the credit policy. Status:Charged Off",
}

STATUS_ALT_DEFAULT = STATUS_DEFAULT | {"Late (31-120 days)"}


DERIVED_COLUMNS = [
    "default_flag",
    "default_flag_alt",
    "desfecho_credito",
    "status_finalizado",
]


def derived_values(loan_status: str) -> dict[str, str]:
    if loan_status in STATUS_DEFAULT:
        return {
            "default_flag": "1",
            "default_flag_alt": "1",
            "desfecho_credito": "inadimplente",
            "status_finalizado": "1",
        }

    if loan_status in STATUS_PAID:
        return {
            "default_flag": "0",
            "default_flag_alt": "0",
            "desfecho_credito": "adimplente",
            "status_finalizado": "1",
        }

    if loan_status in STATUS_ALT_DEFAULT:
        return {
            "default_flag": "",
            "default_flag_alt": "1",
            "desfecho_credito": "em_andamento_nao_finalizado",
            "status_finalizado": "0",
        }

    return {
        "default_flag": "",
        "default_flag_alt": "",
        "desfecho_credito": "em_andamento_nao_finalizado",
        "status_finalizado": "0",
    }


def classify_csv(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(newline="", encoding="utf-8-sig") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError(f"{input_path} has no header")
        if "loan_status" not in reader.fieldnames:
            raise ValueError(f"{input_path} does not contain loan_status")

        base_fields = [name for name in reader.fieldnames if name not in DERIVED_COLUMNS]
        fieldnames = base_fields + DERIVED_COLUMNS

        with output_path.open("w", newline="", encoding="utf-8") as dst:
            writer = csv.DictWriter(dst, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                clean_row = {name: row.get(name, "") for name in base_fields}
                clean_row.update(derived_values(row.get("loan_status", "")))
                writer.writerow(clean_row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    classify_csv(args.input_csv, args.output_csv)


if __name__ == "__main__":
    main()
