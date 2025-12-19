import argparse
import csv
import os
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

from measure_person import measure_person

Metrics = Dict[str, float]

DIMENSIONS = ["shoulder", "waist", "chest", "hip"]
PRED_MAPPING = {
    "shoulder": "shoulder_width_cm",
    "waist": "waist_width_cm",
    "chest": "chest_width_cm",
    "hip": "hip_width_cm",
}


def compute_errors(df: pd.DataFrame) -> Metrics:
    metrics: Metrics = {}
    for dim in DIMENSIONS:
        gt_col = f"{dim}_cm"
        pred_col = f"pred_{dim}_cm"
        if pred_col not in df.columns:
            continue
        sub = df[[gt_col, pred_col]].dropna()
        if sub.empty:
            continue
        abs_err = (sub[gt_col] - sub[pred_col]).abs()
        mae = abs_err.mean()
        # MAPE skip zeros
        non_zero = sub[sub[gt_col] > 0]
        if not non_zero.empty:
            mape = (abs_err[non_zero.index] / non_zero[gt_col] * 100).mean()
        else:
            mape = float("nan")
        metrics[f"{dim}_mae_cm"] = round(mae, 3)
        metrics[f"{dim}_mape_pct"] = round(mape, 2) if mape == mape else float("nan")
    return metrics


def load_ground_truth(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    expected_cols = {"filename", "height_cm"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain at least columns: {expected_cols}")
    return df


def evaluate(images_dir: Path, gt_df: pd.DataFrame, limit: Optional[int] = None) -> pd.DataFrame:
    rows = []
    for i, row in gt_df.iterrows():
        if limit is not None and i >= limit:
            break
        fname = row["filename"]
        height_cm = float(row["height_cm"])
        img_path = images_dir / fname
        if not img_path.exists():
            result = {"filename": fname, "error": "missing_image"}
            rows.append(result)
            continue
        meas = measure_person(str(img_path), real_height_cm=height_cm, draw=False, verbose=False)
        if not meas.get("ok"):
            result = {"filename": fname, "error": meas.get("error", "unknown")}
            rows.append(result)
            continue
        output = {
            "filename": fname,
            "height_cm": height_cm,
            "pixel_to_cm": meas.get("pixel_to_cm"),
            "confidence": meas.get("confidence"),
        }
        # Predictions
        for dim, key in PRED_MAPPING.items():
            output[f"pred_{dim}_cm"] = meas.get(key)
            # Ground truth if present
            gt_key = f"{dim}_cm"
            if gt_key in row and not pd.isna(row[gt_key]):
                output[gt_key] = float(row[gt_key])
        rows.append(output)
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Batch evaluate body measurement predictions.")
    parser.add_argument("--images", required=True, help="Directory with input images")
    parser.add_argument("--csv", required=True, help="Ground truth CSV (filename,height_cm, optional widths)")
    parser.add_argument("--out", default="results.csv", help="Output CSV path")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on number of rows to process")
    args = parser.parse_args()

    images_dir = Path(args.images)
    gt_df = load_ground_truth(Path(args.csv))

    results_df = evaluate(images_dir, gt_df, limit=args.limit)
    metrics = compute_errors(results_df)

    # Aggregate confidence
    if "confidence" in results_df.columns:
        metrics["avg_confidence"] = round(results_df["confidence"].dropna().mean(), 3)

    results_df.to_csv(args.out, index=False)

    print("Saved results:", args.out)
    print("Image count:", len(results_df))
    print("Errors present:", results_df[results_df.get("error").notna()].shape[0] if "error" in results_df.columns else 0)
    print("Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    # Simple suggestion if waist error high
    waist_mape = metrics.get("waist_mape_pct")
    if waist_mape and waist_mape == waist_mape and waist_mape > 8:
        print("NOTE: High waist MAPE; consider multi-slice regression calibration.")

if __name__ == "__main__":
    main()
