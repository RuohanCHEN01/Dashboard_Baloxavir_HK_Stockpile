# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 12:59:20 2026

@author: chenr
"""

import pandas as pd
import numpy as np

input_file = r"C:\Users\chenr\Desktop\Result_Influenza_pandemic\Mar27_2026\Output_dataset\Test_cost_analysis_FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv"
output_file = input_file
wtp = 422242

df = pd.read_csv(input_file)
df.columns = [str(c).strip() for c in df.columns]

# 只保留 A-W 列
df = df.iloc[:, :23].copy()

baseline_mask = (
    pd.to_numeric(df["BXM_proportion"], errors="coerce").round(10).eq(0) &
    pd.to_numeric(df["OTV_proportion"], errors="coerce").round(10).eq(0.9) &
    pd.to_numeric(df["ZNV_proportion"], errors="coerce").round(10).eq(0.1)
)

if baseline_mask.sum() != 1:
    raise ValueError(f"基准行数量不是 1，而是 {baseline_mask.sum()}。请检查数据。")

baseline_total_cost = pd.to_numeric(df.loc[baseline_mask, "Total_cost"], errors="coerce").iloc[0]
baseline_qaly_negative = -pd.to_numeric(df.loc[baseline_mask, "Total_QALY"], errors="coerce").iloc[0]

df["qaly_negative"] = -pd.to_numeric(df["Total_QALY"], errors="coerce")
df["incre_cost"] = pd.to_numeric(df["Total_cost"], errors="coerce") - baseline_total_cost
df["incre_qaly"] = df["qaly_negative"] - baseline_qaly_negative
df["icer"] = df["incre_cost"] / df["incre_qaly"]
df["negative_situation"] = np.where(df["incre_cost"] > 0, "dominated", "dominating")
df["inmb"] = (wtp * df["incre_qaly"]) - df["incre_cost"]

# 基准行 X-AC 显示为空
new_cols = ["qaly_negative", "incre_cost", "incre_qaly", "icer", "negative_situation", "inmb"]
for col in new_cols:
    df[col] = df[col].astype("object")
df.loc[baseline_mask, new_cols] = ""

df.to_csv(output_file, index=False, encoding="utf-8-sig")
