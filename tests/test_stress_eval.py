import argparse
from os.path import join

from codalab.evaluation import parse_data, do_eval_core
from tests.utils import DATA_DIR, create_submission, to_jsonl


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Launch random stress-test for evaluation")

    parser.add_argument('-g', '--gold', default=join(DATA_DIR, "validation_labeled.jsonl"), type=str)
    parser.add_argument('-p', '--predict', default=join(DATA_DIR, "validation.jsonl"), type=str)
    parser.add_argument('-a', '--attempts', default=100, type=int)
    parser.add_argument('-m', '--max_opinions', default=50, type=int)
    parser.add_argument('-l', '--labels', default=["POS", "NEG"], type=list)
    parser.add_argument('-s', '--save_latest', default="submission.jsonl", type=str)

    args = parser.parse_args()

    for i in range(args.attempts):

        preds = create_submission(load_data_func=lambda: parse_data(args.predict),
                                  ops_max_count=args.max_opinions,
                                  polarities=args.labels)

        if args.save_latest is not None:
            to_jsonl(data=preds, target=args.save_latest)

        f1 = do_eval_core(gold=parse_data(args.gold), preds=preds)

        print(f"TEST-{i}:", f1)
