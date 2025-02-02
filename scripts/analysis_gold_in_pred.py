import argparse
from os.path import join, basename

from codalab.evaluation import parse_data
from scripts.utils import iter_dir_filepaths, iter_submission_lines, dict_register_path, dict_dfs_traversal, \
    dict_try_get, spreadsheet_format_line
from tests.utils import DATA_DIR


def opinion_end_to_str(item):
    assert(check_opinion_ends(item))
    return item[0][0]


def check_opinion_ends(item):
    return len(item) == 2 and len(item[0]) == 1


def index_submission(sentences):
    """ This methods perform flattening of the data.
    """
    index = {}
    for sentence in sentences:
        for opinion in sentence['opinions']:
            # We simplify our analysis for the particular cases of Source and Target entries.
            if not check_opinion_ends(opinion["Source"]) or not check_opinion_ends(opinion["Target"]):
                continue
            v = dict_register_path(index,
                                   # This is how we flattening the dictionary.
                                   # We use SENTENCE_ID, SOURCE, TARGET.
                                   path=[sentence["sent_id"],
                                         opinion_end_to_str(opinion["Source"]),
                                         opinion_end_to_str(opinion["Target"])],
                                   value_if_not_exist=dict())
            # Save initial label.
            v["label"] = opinion["Polarity"]
    return index


def do_analysis_a_in_b(a_index, b_index, stat):
    for registered_opinion, pred_label in dict_dfs_traversal(a_index):
        path_to_node = registered_opinion[:-1]

        # If the related opinion exist.
        gold_node = dict_try_get(b_index, path_to_node)
        is_exist = gold_node is not None
        is_exist_label = gold_node["label"] == pred_label if gold_node is not None else False

        # register opinion existence.
        stat_is_exist = dict_register_path(stat, path_to_node + ["is_exist"], value_if_not_exist=[])
        stat_is_exist.append('+' if is_exist else '-')

        # register opinion exact match.
        stat_is_exist = dict_register_path(stat, path_to_node + ["is_exist_label"], value_if_not_exist=[])
        stat_is_exist.append('+' if is_exist_label else '-')


def submission_name(fp):
    return basename(fp).split('_')[1].split('.zip')[0]


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Analysis of the codalab submissions for RuOpinionNE-2024."
                                     "This script covers presence of the gold data in submissions (pred).")

    parser.add_argument('-g', '--gold', default=join(DATA_DIR, "submissions/test_labeled.jsonl"), type=str)
    parser.add_argument('-p', '--submissions_dir', default=join(DATA_DIR, "submissions"), type=str)

    args = parser.parse_args()

    gold_index = index_submission(parse_data(args.gold))

    subs_iter = iter_dir_filepaths(from_dir=args.submissions_dir,
                                   filter_full_path=lambda item: item.endswith(".zip"))
    submissions_filepaths = list(subs_iter)

    # Perform analysis.
    STAT_GOLD_IN_PRED = dict()
    for submission_filepath in submissions_filepaths:
        pred = parse_data(submission_filepath, iter_json_func=iter_submission_lines)
        do_analysis_a_in_b(gold_index, index_submission(pred), stat=STAT_GOLD_IN_PRED)

    # Output the results.
    for mode in ["is_exist", "is_exist_label"]:

        with open(f"analysis_gold_in_pred_{mode}.tsv", "w") as out:

            header = spreadsheet_format_line(["sent_id", "Source", "Target"] +
                                             [submission_name(fp) for fp in submissions_filepaths])

            out.write(header)
            for registered_opinion, v in dict_dfs_traversal(STAT_GOLD_IN_PRED):
                if registered_opinion[-1] != mode:
                    continue
                out.write(spreadsheet_format_line(registered_opinion[:-1] + v))
