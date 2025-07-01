# -*- coding: utf-8 -*-
"""
Updated on May 15, 2025

Reads all PDF leaf test reports in a folder, extracts nutrient data,
calculates deviation and score (with stronger penalty for large deviations,
and zero score for deviations >= 250%),
and prints summary tables.

@author: Franz Hentze
"""

import fitz  # PyMuPDF
import re
import os
import pandas as pd
import numpy as np
from datetime import datetime

def smooth_score(deviation, D=50, n=2, cutoff=250):
    """
    Calculate a smooth score from deviation (%).
    Scores are 100 at 0 deviation, decrease quadratically,
    and are zero if deviation >= cutoff (in %).
    """
    x = abs(deviation) * 100  # Convert fraction to percentage
    if x >= cutoff:
        return 0
    score = 100 / (1 + (x / D)**n)
    return max(min(score, 100), 0)


def extract_reports(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    raw_sections = text.split("PADDOCK:")

    expected_nutrients = [
        "N - Nitrogen", "P - Phosphorus", "K - Potassium", "S - Sulphur",
        "Ca - Calcium", "Mg - Magnesium", "Na - Sodium", "Cu - Copper",
        "Zn - Zinc", "Mn - Manganese", "Fe - Iron", "B - Boron",
        "Mo - Molybdenum", "Si - Silicon", "Co - Cobalt"
    ]

    reports = []

    for section in raw_sections[1:]:
        lines = section.splitlines()

        paddock = next((line.strip() for line in lines if line.strip()), "Unknown")
        paddock = paddock.replace("“", "\"").replace("”", "\"").replace("–", "-")

        actual_values = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if any(n in line for n in expected_nutrients):
                nutrient = line
                j = i + 1
                while j < len(lines):
                    val_line = lines[j].strip()
                    try:
                        value = float(val_line)
                        actual_values.append((nutrient, value))
                        break
                    except ValueError:
                        j += 1
                i = j
            else:
                i += 1

        actual_values = actual_values[:15]

        if "Plant TherapyTM" not in section:
            print(f"⚠️ Skipping paddock '{paddock}' – no ideal range block.")
            continue

        range_block = section.split("Plant TherapyTM")[1]
        range_lines = range_block.splitlines()
        range_values = []
        for line in range_lines:
            line = line.strip()
            if "N/A" in line:
                continue
            match = re.match(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", line)
            if match:
                range_values.append((float(match.group(1)), float(match.group(2))))

        if len(range_values) == 0:
            print(f"⚠️ Skipping paddock '{paddock}' – no usable ranges found.")
            continue

        nutrients = []
        for (label, actual), (min_val, max_val) in zip(actual_values[:len(range_values)], range_values):
            # Adjust ideal: use max for P, Ca, Mg, B; else average
            if any(x in label for x in ["P - Phosphorus", "Ca - Calcium", "Mg - Magnesium", "B - Boron"]):
                ideal = max_val
            else:
                ideal = (min_val + max_val) / 2

            deviation = (actual - ideal) / ideal
            score = smooth_score(deviation)  # deviation is a fraction here

            nutrients.append({
                "Nutrient": label,
                "Actual": actual,
                "Min": min_val,
                "Max": max_val,
                "Ideal": ideal,
                "Deviation (%)": round(deviation * 100, 2),
                "Score": round(score, 2)
            })

        reports.append({
            "paddock": paddock,
            "nutrients": nutrients
        })

    return reports


def print_summary_score_table(all_reports):
    paddock_scores = []

    for report in all_reports:
        df = pd.DataFrame(report["nutrients"])
        score = round(df["Score"].mean(), 2)
        filename = report.get("source_file", "N/A")
        paddock_scores.append((report["paddock"], score, filename))

    sorted_scores = sorted(paddock_scores, key=lambda x: x[1])

    print("\n📊 Summary Table – General Nutritional Scores (Lowest to Highest):\n")
    print(f"{'':>3} {'Paddock':<30} {'Score':>6}   {'Source File'}")
    for i, (paddock, score, filename) in enumerate(sorted_scores, 1):
        print(f"{i:>3}. {paddock:<30} {score:>6.2f}   {filename}")

    summary_df = pd.DataFrame(sorted_scores, columns=["Paddock", "General Score", "Source File"])
    return summary_df


def process_all_pdfs(folder_path):
    all_data = []
    all_reports = []

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("❌ No PDF files found in the folder.")
        return

    print(f"📁 Found {len(pdf_files)} PDF(s) to process.")

    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        print(f"\n📄 Processing: {filename}")
        reports = extract_reports(pdf_path)

        for report in reports:
            df = pd.DataFrame(report["nutrients"])
            general_score = round(df["Score"].mean(), 2)

            print(f"📍 Paddock: {report['paddock']}")
            print(df.to_string(index=False))
            print(f"🌿 General Nutritional Score: {general_score}/100\n")

            df.insert(0, "Paddock", report["paddock"])
            df["General Score"] = general_score
            all_data.append(df)

            report["source_file"] = filename
            all_reports.append(report)

    if all_data:
        summary_df = print_summary_score_table(all_reports)
    else:
        print("❌ No valid data extracted.")


if __name__ == "__main__":
    folder_path = ".\\"
    process_all_pdfs(folder_path)

