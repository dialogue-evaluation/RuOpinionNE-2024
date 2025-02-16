import argparse
from os.path import join

from analysis.analysis_gold_in_pred import submission_name
from analysis.utils import ANALYSIS_DIR, iter_dir_filepaths, iter_submission_lines, spreadsheet_format_line
from codalab.evaluation import do_eval_core, parse_data, UNKN_ORIGIN
from tests.utils import DATA_DIR


def replace_author_to_null(row_dict):
    assert(isinstance(row_dict, dict))
    for opinion in row_dict["opinions"]:
        for end_type in ["Source", "Target"]:
            for attribute in opinion[end_type]:
                if attribute[0] == "AUTHOR":
                    attribute[0] = UNKN_ORIGIN
    return row_dict


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Post-evaluation result analysis.")

    parser.add_argument('-g', '--gold', default=join(DATA_DIR, "./validation_labeled.jsonl"), type=str)
    parser.add_argument('-p', '--submissions_dir', default=join(ANALYSIS_DIR, "submissions"), type=str)
    parser.add_argument('--handle_mode', default="author-to-none", choices=["author-to-none", "none"], type=str)

    args = parser.parse_args()

    handler = None
    if args.handle_mode == "author-to-none":
        handler = replace_author_to_null
    print("Using handler:", handler)

    gold = parse_data(args.gold, handle_lines_func=handler)

    subs_iter = iter_dir_filepaths(from_dir=args.submissions_dir,
                                   filter_full_path=lambda item: item.endswith(".zip"))

    results = []
    for submission_filepath in subs_iter:
        pred = parse_data(submission_filepath, iter_json_func=iter_submission_lines, handle_lines_func=handler)
        f1 = do_eval_core(gold=gold, preds=pred)
        results.append([submission_name(submission_filepath), round(f1, 3)])

    for item in sorted(results, key=lambda item: item[1], reverse=True):
        print(spreadsheet_format_line(item, new_line=False))