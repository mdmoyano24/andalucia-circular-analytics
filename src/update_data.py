# src/update_data.py
"""
Update & tidy datasets for andalucia-circular-analytics.

- Funciona como script CLI (python -m src.update_data ...).
- Puede importarse desde notebooks: from src.update_data import pull_all, pull_eurostat, process_esoc

Salidas:
  data/external/eurostat_env_wasmun_ES_UE.csv
  data/external/eurostat_env_waspac_ES_UE.csv
  data/processed/es_ue_residuos_reciclaje.csv
  (si hay ESOC en data/raw/) data/processed/esoc2023_*.csv
"""

from __future__ import annotations
from pathlib import Path
import sys
import argparse
import pandas as pd
from typing import List

# --- paths ---
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
EXT = DATA / "external"
PROC = DATA / "processed"
EXT.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)


# ---------- helpers ----------
def _detect_year_cols(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if str(c).isdigit()]

def _to_long(df: pd.DataFrame, id_vars: List[str]) -> pd.DataFrame:
    year_cols = _detect_year_cols(df)
    return df.melt(id_vars=id_vars, value_vars=year_cols, var_name="year", value_name="value")

def _coerce_year_value(df: pd.DataFrame) -> pd.DataFrame:
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df.dropna(subset=["value"])

def _safe_save(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✔ saved: {path.relative_to(ROOT)}")


# ---------- eurostat pulls ----------
def pull_eurostat_wasmun() -> pd.DataFrame:
    """
    env_wasmun – municipal waste per capita (kg/hab), operation GEN.
    Devuelve ES & EU27_2020 en formato largo con columnas: geo, year, residuos_kg_hab
    """
    try:
        import eurostat
    except ImportError as e:
        raise RuntimeError("Falta el paquete 'eurostat'. Instala con: pip install eurostat") from e

    df = eurostat.get_data_df("env_wasmun", flags=False).reset_index()

    # renombrar geo si viene con backslash
    if "geo\\TIME_PERIOD" in df.columns:
        df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

    id_vars = [c for c in ["geo", "wst_oper", "unit"] if c in df.columns]
    long = _to_long(df, id_vars=id_vars)
    long = _coerce_year_value(long)

    filt = (
        (long["unit"] == "KG_HAB")
        & (long["wst_oper"] == "GEN")
        & (long["geo"].isin(["ES", "EU27_2020"]))
    )
    out = long.loc[filt, ["geo", "year", "value"]].rename(columns={"value": "residuos_kg_hab"})
    _safe_save(out, EXT / "eurostat_env_wasmun_ES_UE.csv")
    return out


def pull_eurostat_waspac() -> pd.DataFrame:
    """
    env_waspac – packaging recycling rate (%), W1501 total packaging, operation RCV.
    Devuelve ES & EU27_2020 en formato largo con columnas: geo, year, reciclaje_envases_pct
    """
    try:
        import eurostat
    except ImportError as e:
        raise RuntimeError("Falta el paquete 'eurostat'. Instala con: pip install eurostat") from e

    df = eurostat.get_data_df("env_waspac", flags=False).reset_index()
    if "geo\\TIME_PERIOD" in df.columns:
        df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

    id_vars = [c for c in ["geo", "waste", "wst_oper", "unit"] if c in df.columns]
    long = _to_long(df, id_vars=id_vars)
    long = _coerce_year_value(long)

    filt = (
        (long["geo"].isin(["ES", "EU27_2020"])) &
        (long["unit"] == "PC") &
        (long["waste"] == "W1501") &    # total packaging
        (long["wst_oper"] == "RCV")     # recycled
    )
    sliced = long.loc[filt, ["geo", "year", "value"]].rename(columns={"value": "reciclaje_envases_pct"})
    _safe_save(sliced, EXT / "eurostat_env_waspac_ES_UE.csv")
    return sliced


def pull_eurostat(join: bool = True) -> pd.DataFrame:
    """
    Descarga y guarda ambos datasets. Si join=True, devuelve y guarda el merge en processed/.
    """
    wasmun = pull_eurostat_wasmun()
    waspac = pull_eurostat_waspac()

    if join:
        merged = pd.merge(wasmun, waspac, on=["geo", "year"], how="outer").sort_values(["geo", "year"])
        _safe_save(merged, PROC / "es_ue_residuos_reciclaje.csv")
        return merged
    return wasmun


# ---------- ESOC (opcional) ----------
def process_esoc() -> None:
    """
    Procesa microdatos ESOC 2023 si existen:
      - motivos desechar alimentos (respalim) [% ponderado con fep]
      - medidas reducción residuos (medida1..8) [%]
    """
    csv = RAW / "md_ESOC2023.csv"
    if not csv.exists():
        print("ℹ ESOC: no encontrado data/raw/md_ESOC2023.csv — saltando.")
        return

    df = pd.read_csv(csv, sep=";", encoding="utf-8-sig", low_memory=False)
    if "fep" not in df.columns:
        print("⚠ ESOC: no existe 'fep'; se asume peso 1.")
        df["fep"] = 1.0
    peso = df["fep"].astype(float)

    def wcounts(series: pd.Series) -> pd.Series:
        w = peso.groupby(series).sum().sort_values(ascending=False)
        return (w / peso.sum() * 100).round(1)

    # motivos desechar alimentos
    if "respalim" in df.columns:
        tab = wcounts(df["respalim"]).rename("pct").reset_index().rename(columns={"index": "respalim"})
        _safe_save(tab, PROC / "esoc2023_motivos_desechar_alimentos_pct.csv")

    # medidas reducción residuos
    medidas = [c for c in df.columns if c.lower().startswith("medida")]
    if medidas:
        res = {}
        wtot = peso.sum()
        for c in medidas:
            res[c] = float(((df[c] == 1).astype(int) * peso).sum() / wtot * 100)
        series = pd.Series(res, name="pct").sort_values(ascending=False)
        _safe_save(series.reset_index().rename(columns={"index": "medida"}), PROC / "esoc2023_medidas_reduccion_pct.csv")


def pull_all() -> pd.DataFrame:
    """
    Ejecuta todo: Eurostat (con join) y ESOC (si está disponible).
    Devuelve el DF combinado ES/UE residuos+reciclaje.
    """
    merged = pull_eurostat(join=True)
    process_esoc()
    return merged


# ---------- CLI ----------
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Update & tidy datasets for andalucia-circular-analytics")
    sub = p.add_subparsers(dest="cmd", required=False)

    sub.add_parser("eurostat", help="Descarga Eurostat (env_wasmun & env_waspac) y guarda CSVs")
    sub.add_parser("esoc", help="Procesa ESOC 2023 si el CSV está en data/raw/")
    sub.add_parser("all", help="Eurostat + ESOC y guarda outputs")

    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    # default: all
    if args.cmd in (None, "all"):
        pull_all()
    elif args.cmd == "eurostat":
        pull_eurostat(join=True)
    elif args.cmd == "esoc":
        process_esoc()
    else:
        print("Comando no reconocido. Usa --help.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
