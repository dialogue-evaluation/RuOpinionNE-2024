import csv

import pandas as pd


def concatenate_csvs(filepaths, output_file):
    assert(len(filepaths) >= 2)

    pds = []

    # first file.
    df = pd.read_csv(filepaths[0], sep='\t', quoting=csv.QUOTE_NONE, encoding='utf-8')
    df = df.drop(columns=["rendering"])
    pds.append(df)

    # We keep all the files except rendering column.
    for f in filepaths[1:-1]:
        df = pd.read_csv(f, sep='\t', quoting=csv.QUOTE_NONE, encoding='utf-8')
        df = df.drop(columns=["sent_id", "Source", "Target", "rendering"])
        pds.append(df)

    # in last file we pick rendering.
    df = pd.read_csv(filepaths[-1], sep='\t', quoting=csv.QUOTE_NONE, encoding='utf-8')
    df = df.drop(columns=["sent_id", "Source", "Target"])
    pds.append(df)

    df_combined = pd.concat(pds, axis=1)
    df_combined.to_csv(output_file, sep='\t', index=False)


if __name__ == '__main__':
    concatenate_csvs(["analysis_gold_in_pred_is_exist.tsv",
                      "analysis_gold_in_pred_is_exist_label.tsv",
                      "analysis_gold_in_pred_used_span.tsv",
                      "analysis_gold_in_pred_used_span_region.tsv"],
                     output_file="analysis_gold_full.tsv")

    concatenate_csvs(["analysis_pred_not_in_gold_is_exist.tsv",
                      "analysis_pred_not_in_gold_used_span.tsv",
                      "analysis_pred_not_in_gold_used_span_region.tsv"],
                     output_file="analysis_missed.tsv")
