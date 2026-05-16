"""Deterministic validation for FinLend LLM credit-risk claims.

The main validation uses the same analytical universe as the canonical
notebook: full available Lending Club period, loans with known final outcome,
and loan-level metrics.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


RELEVANT_COLUMNS = [
    "purpose",
    "loan_status",
    "loan_amnt",
    "funded_amnt",
    "annual_inc",
    "grade",
    "sub_grade",
    "int_rate",
    "issue_d",
    "dti",
]

NON_DEFAULT_STATUSES = {
    "Fully Paid",
    "Does not meet the credit policy. Status:Fully Paid",
}

DEFAULT_STATUSES = {
    "Charged Off",
    "Default",
    "Does not meet the credit policy. Status:Charged Off",
}

AMBIGUOUS_STATUSES = {
    "Current",
    "In Grace Period",
    "Late (16-30 days)",
    "Late (31-120 days)",
    "Issued",
}


@dataclass(frozen=True)
class MetricClaim:
    metric: str
    llm_value: float
    metric_type: str
    unit: str
    observation: str


LLM_CLAIMS = [
    MetricClaim(
        "Share debt_consolidation",
        48.0,
        "percentage",
        "%",
        "Agente afirma 48% da carteira total.",
    ),
    MetricClaim(
        "Default rate debt_consolidation",
        12.3,
        "percentage",
        "%",
        "Taxa depende da regra de default e base elegivel.",
    ),
    MetricClaim(
        "Default rate overall",
        14.1,
        "percentage",
        "%",
        "Usada pelo agente para afirmar que o segmento esta abaixo da media.",
    ),
    MetricClaim(
        "Average ticket debt_consolidation",
        72_000.0,
        "money",
        "USD",
        "No enunciado, o agente informa ticket medio de 72.000.",
    ),
    MetricClaim(
        "Average annual income debt_consolidation",
        15_200.0,
        "money",
        "USD/year",
        "No enunciado, o agente informa renda media anual de 15.200.",
    ),
    MetricClaim(
        "Share grade B or C debt_consolidation",
        62.0,
        "distribution",
        "%",
        "Distribuicao de grade no segmento.",
    ),
    MetricClaim(
        "Average interest rate debt_consolidation",
        13.8,
        "mean",
        "%",
        "Media simples da taxa contratada.",
    ),
]


def classify_status(status: Any, include_late_31_as_default: bool = False) -> str:
    """Map raw Lending Club loan_status to validation categories."""
    if pd.isna(status):
        return "unknown"

    status = str(status).strip()
    default_statuses = set(DEFAULT_STATUSES)
    ambiguous_statuses = set(AMBIGUOUS_STATUSES)

    if include_late_31_as_default:
        default_statuses.add("Late (31-120 days)")
        ambiguous_statuses.discard("Late (31-120 days)")

    if status in default_statuses:
        return "default"
    if status in NON_DEFAULT_STATUSES:
        return "non_default"
    if status in ambiguous_statuses:
        return "ambiguous"
    return "unknown"


def load_lending_club(path: str | Path) -> pd.DataFrame:
    """Read only the fields required for the validation."""
    path = Path(path)
    df = pd.read_csv(path, usecols=lambda col: col in RELEVANT_COLUMNS, low_memory=False)
    df.columns = [col.strip().lower() for col in df.columns]

    for col in RELEVANT_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    df["int_rate"] = pd.to_numeric(
        df["int_rate"].astype(str).str.replace("%", "", regex=False).str.strip(),
        errors="coerce",
    )
    df["loan_amnt"] = pd.to_numeric(df["loan_amnt"], errors="coerce")
    df["funded_amnt"] = pd.to_numeric(df["funded_amnt"], errors="coerce")
    df["annual_inc"] = pd.to_numeric(df["annual_inc"], errors="coerce")
    df["dti"] = pd.to_numeric(df["dti"], errors="coerce")
    df["issue_date"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
    df["issue_year"] = df["issue_date"].dt.year
    return df


def prepare_validation_base(
    df: pd.DataFrame,
    include_late_31_as_default: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Create the eligible loan-level base used as ground truth."""
    prepared = df.copy()
    prepared["status_category"] = prepared["loan_status"].apply(
        classify_status, include_late_31_as_default=include_late_31_as_default
    )

    counts = prepared["status_category"].value_counts(dropna=False).to_dict()
    eligible = prepared[prepared["status_category"].isin(["default", "non_default"])].copy()
    eligible["default_flag"] = (eligible["status_category"] == "default").astype(int)

    metadata = {
        "raw_rows": len(prepared),
        "eligible_rows": len(eligible),
        "excluded_rows": len(prepared) - len(eligible),
        "status_category_counts": counts,
        "period_min": int(eligible["issue_year"].min()),
        "period_max": int(eligible["issue_year"].max()),
        "include_late_31_as_default": include_late_31_as_default,
    }
    return eligible, metadata


def calculate_ground_truth(df: pd.DataFrame) -> dict[str, float]:
    """Calculate official deterministic metrics for debt_consolidation."""
    segment = df[df["purpose"].eq("debt_consolidation")].copy()
    return {
        "Share debt_consolidation": len(segment) / len(df) * 100,
        "Default rate debt_consolidation": segment["default_flag"].mean() * 100,
        "Default rate overall": df["default_flag"].mean() * 100,
        "Average ticket debt_consolidation": segment["loan_amnt"].mean(),
        "Average funded amount debt_consolidation": segment["funded_amnt"].mean(),
        "Average annual income debt_consolidation": segment["annual_inc"].mean(),
        "Share grade B or C debt_consolidation": segment["grade"].isin(["B", "C"]).mean() * 100,
        "Average interest rate debt_consolidation": segment["int_rate"].mean(),
        "Segment N": float(len(segment)),
        "Eligible N": float(len(df)),
    }


def classify_divergence(
    llm_value: float,
    calculated_value: float,
    metric_type: str,
) -> tuple[str, str, float, float]:
    """Apply validation tolerances by metric type."""
    abs_diff = calculated_value - llm_value
    pct_diff = abs_diff / abs(llm_value) * 100 if llm_value else np.nan

    if pd.isna(calculated_value):
        return "Nao verificavel", "Metrica nao calculavel com os campos disponiveis.", abs_diff, pct_diff

    if metric_type == "percentage":
        if abs(abs_diff) <= 1:
            return "OK", "Dentro da tolerancia de 1 p.p.", abs_diff, pct_diff
        if abs(abs_diff) > 5:
            return "Critico", "Divergencia acima de 5 p.p.", abs_diff, pct_diff
        return "Divergente", "Fora da tolerancia de 1 p.p.", abs_diff, pct_diff

    if metric_type == "distribution":
        if abs(abs_diff) <= 2:
            return "OK", "Dentro da tolerancia de 2 p.p.", abs_diff, pct_diff
        if abs(abs_diff) > 5:
            return "Critico", "Divergencia relevante na distribuicao.", abs_diff, pct_diff
        return "Divergente", "Fora da tolerancia de 2 p.p.", abs_diff, pct_diff

    if metric_type in {"money", "mean"}:
        rel_diff = abs(abs_diff) / abs(calculated_value) if calculated_value else np.nan
        if rel_diff <= 0.05:
            return "OK", "Dentro da tolerancia relativa de 5%.", abs_diff, pct_diff
        if rel_diff > 0.20:
            return "Critico", "Divergencia relativa acima de 20%.", abs_diff, pct_diff
        return "Divergente", "Fora da tolerancia relativa de 5%.", abs_diff, pct_diff

    return "Nao verificavel", "Tipo de metrica sem regra de tolerancia.", abs_diff, pct_diff


def build_validation_table(metrics: dict[str, float]) -> pd.DataFrame:
    rows = []
    for claim in LLM_CLAIMS:
        calculated = metrics.get(claim.metric, np.nan)
        status, note, abs_diff, pct_diff = classify_divergence(
            claim.llm_value, calculated, claim.metric_type
        )
        rows.append(
            {
                "metrica": claim.metric,
                "valor_llm": claim.llm_value,
                "valor_calculado": calculated,
                "diferenca_absoluta": abs_diff,
                "diferenca_percentual": pct_diff,
                "status": status,
                "observacao": f"{claim.observation} {note}",
            }
        )
    return pd.DataFrame(rows)


def plot_validation_results(validation: pd.DataFrame, output_path: str | Path) -> None:
    """Create a simple status-count chart for documentation."""
    import matplotlib.pyplot as plt

    counts = validation["status"].value_counts().reindex(
        ["OK", "Divergente", "Critico", "Nao verificavel"], fill_value=0
    )
    colors = {
        "OK": "#2ecc71",
        "Divergente": "#f39c12",
        "Critico": "#e74c3c",
        "Nao verificavel": "#95a5a6",
    }

    fig, ax = plt.subplots(figsize=(7, 4))
    counts.plot(kind="bar", ax=ax, color=[colors[idx] for idx in counts.index])
    ax.set_title("Validacao dos claims quantitativos do agente")
    ax.set_xlabel("Status")
    ax.set_ylabel("Numero de claims")
    ax.tick_params(axis="x", rotation=0)
    for idx, value in enumerate(counts):
        ax.text(idx, value + 0.05, str(value), ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", dpi=140)
    plt.close(fig)


def qualitative_rule_check(answer_context: dict[str, bool]) -> dict[str, str]:
    """Simple deterministic checks for answer quality."""
    rules = {
        "has_period": "Periodo analisado informado",
        "has_unit_of_analysis": "Unidade de analise informada",
        "has_default_definition": "Definicao de inadimplencia informada",
        "has_denominator": "N absoluto/denominador informado",
        "has_currency_and_scale": "Moeda e escala monetaria informadas",
        "has_traceability": "Query, calculo ou fonte rastreavel informada",
        "avoids_causality": "Nao afirma causalidade indevida",
    }
    return {
        name: "OK" if answer_context.get(name, False) else "Alerta"
        for name in rules
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/raw/loan.csv")
    parser.add_argument("--include-late-31-default", action="store_true")
    parser.add_argument("--plot", default=None, help="Optional path for a status-count chart.")
    args = parser.parse_args()

    raw = load_lending_club(args.csv)
    base, metadata = prepare_validation_base(
        raw,
        include_late_31_as_default=args.include_late_31_default,
    )
    metrics = calculate_ground_truth(base)
    validation = build_validation_table(metrics)

    print("Metadata")
    for key, value in metadata.items():
        print(f"- {key}: {value}")

    print("\nGround truth")
    for key, value in metrics.items():
        print(f"- {key}: {value:,.4f}")

    print("\nValidation table")
    print(validation.to_string(index=False))

    if args.plot:
        plot_validation_results(validation, args.plot)
        print(f"\nChart saved to {args.plot}")


if __name__ == "__main__":
    main()
