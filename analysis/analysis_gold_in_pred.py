import argparse
from os.path import join, basename

from analysis.utils import ANALYSIS_DIR
from codalab.evaluation import parse_data, parse_span, UNKN_ORIGIN
from scripts.utils import iter_dir_filepaths, iter_submission_lines, dict_register_path, dict_dfs_traversal, \
    dict_try_get, spreadsheet_format_line, uppercase_substring, bracket_substring
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
            # Save label.
            v["label"] = opinion["Polarity"]
            # Save span.
            v["span_value"] = opinion["Polar_expression"][0][0]
            v["span_region"] = opinion["Polar_expression"][1][0]
            # Other metadata.
            v["source_region"] = opinion["Source"][1][0]
            v["target_region"] = opinion["Target"][1][0]
            v["text"] = sentence["text"]

    return index


def do_analysis_a_in_b(a_index, b_index, stat):

    for a_opinion, a_label in dict_dfs_traversal(a_index):

        key = a_opinion[-1]
        path_to_node = a_opinion[:-1]
        b_node = dict_try_get(b_index, path_to_node)
        is_exist = b_node is not None

        if key == "label":
            # If the related opinion exist.
            is_exist_label = b_node["label"] == a_label if b_node is not None else False

            # register opinion existence.
            stat_is_exist = dict_register_path(stat, path_to_node + ["is_exist"], value_if_not_exist=[])
            stat_is_exist.append('+' if is_exist else '-')

            # register opinion exact match.
            stat_is_exist = dict_register_path(stat, path_to_node + ["is_exist_label"], value_if_not_exist=[])
            stat_is_exist.append('+' if is_exist_label else '-')
        elif key == "span_value":
            # register the span
            stat_span_value = dict_register_path(stat, path_to_node + ["used_span"], value_if_not_exist=[])
            stat_span_value.append(b_node["span_value"] if is_exist else '-')
        elif key == "span_region":
            stat_span_value = dict_register_path(stat, path_to_node + ["used_span_region"], value_if_not_exist=[])
            stat_span_value.append(b_node["span_region"] if is_exist else '-')
        elif key in ['source_region', 'target_region', 'text']:
            pass
        else:
            raise Exception(f"key=`{key}` handler has not been found!")


def submission_name(fp):
    return basename(fp).split('.zip')[0]


def render_opinion(index_node, highlight_span=True):
    assert(isinstance(index_node, dict))

    text = index_node["text"]
    for r in [index_node["source_region"], index_node["target_region"]]:

        # We do not emphasize UNKN.
        if r == UNKN_ORIGIN:
            continue

        r_from, r_to = parse_span(r)
        text = uppercase_substring(s=text, start=r_from, end=r_to)

    # Replacing the span.
    if highlight_span:
        r_from, r_to = parse_span(index_node["span_region"])
        text = bracket_substring(s=text, start=r_from, end=r_to)

    return text


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Analysis of the codalab submissions for RuOpinionNE-2024."
                                     "This script covers presence of the gold data in submissions (pred).")

    parser.add_argument('-g', '--gold', default=join(DATA_DIR, "./validation_labeled.jsonl"), type=str)
    parser.add_argument('-p', '--submissions_dir', default=join(ANALYSIS_DIR, "submissions"), type=str)

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
    for mode in ["is_exist", "is_exist_label", "used_span", "used_span_region"]:

        with open(f"analysis_gold_in_pred_{mode}.tsv", "w") as out:

            header = spreadsheet_format_line(["sent_id", "Source", "Target"] +
                                             [submission_name(fp) for fp in submissions_filepaths] +
                                             ["rendering"])

            out.write(header)
            for registered_opinion, v in dict_dfs_traversal(STAT_GOLD_IN_PRED):

                pth = registered_opinion[:-1]

                if registered_opinion[-1] != mode:
                    continue

                comment = render_opinion(dict_try_get(d=gold_index, path=pth))
                out.write(spreadsheet_format_line(pth + v + [comment]))
