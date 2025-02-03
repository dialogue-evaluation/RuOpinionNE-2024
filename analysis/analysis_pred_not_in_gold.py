import argparse
from os.path import join

from analysis.utils import ANALYSIS_DIR
from codalab.evaluation import parse_data
from analysis.analysis_gold_in_pred import index_submission, do_analysis_a_in_b, submission_name, render_opinion
from analysis.utils import iter_dir_filepaths, iter_submission_lines, flatten, dict_dfs_traversal, dict_try_get, \
    dict_register_path, spreadsheet_format_line
from tests.utils import DATA_DIR


def index_submission_substract(a_index, b_index):
    """ performs substraction a_index - b_index
    """
    index = {}
    for a_path, a_value in dict_dfs_traversal(a_index):
        if dict_try_get(b_index, a_path) is not None:
            continue
        dict_register_path(index, a_path, a_value)
    return index


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Analysis of the codalab submissions for RuOpinionNE-2024."
                                     "This script covers opinions were absent in gold")

    parser.add_argument('-g', '--gold', default=join(DATA_DIR, "./validation_labeled.jsonl"), type=str)
    parser.add_argument('-p', '--submissions_dir', default=join(ANALYSIS_DIR, "submissions"), type=str)

    args = parser.parse_args()

    # Peform analysis.
    STAT_GOLD_MISSED = dict()

    subs_iter = iter_dir_filepaths(from_dir=args.submissions_dir,
                                   filter_full_path=lambda item: item.endswith(".zip"))
    submissions_filepaths = list(subs_iter)

    # Just reading all the submissions.
    preds = []
    for submission_filepath in submissions_filepaths:
        preds.append(parse_data(submission_filepath, iter_json_func=iter_submission_lines))

    # Index all the submissions as a single instance.
    all_pred_index = index_submission(flatten(preds))
    gold_index = index_submission(parse_data(args.gold))
    all_pred_gold_missed_index = index_submission_substract(all_pred_index, gold_index)

    STAT_PRED_NOT_IN_GOLD = dict()
    for submission_filepath in submissions_filepaths:
        pred = parse_data(submission_filepath, iter_json_func=iter_submission_lines)
        do_analysis_a_in_b(all_pred_gold_missed_index, index_submission(pred), stat=STAT_PRED_NOT_IN_GOLD)

    # Output the results.
    for mode in ["is_exist", "used_span", "used_span_region"]:

        with open(f"analysis_pred_not_in_gold_{mode}.tsv", "w") as out:

            header = spreadsheet_format_line(["sent_id", "Source", "Target"] +
                                             [submission_name(fp) for fp in submissions_filepaths] +
                                             ["rendering"])

            out.write(header)
            for registered_opinion, v in dict_dfs_traversal(STAT_PRED_NOT_IN_GOLD):

                pth = registered_opinion[:-1]

                if registered_opinion[-1] != mode:
                    continue

                comment = render_opinion(dict_try_get(d=all_pred_gold_missed_index, path=pth), highlight_span=False)
                out.write(spreadsheet_format_line(pth + v + [comment]))
