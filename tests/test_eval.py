import sys
import argparse

sys.path.append("../codalab")

from codalab.evaluation import do_eval_core, parse_data


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Launch evaluation process")

    parser.add_argument('-g', '--gold', default="../train.jsonl", type=str)
    parser.add_argument('-p', '--predict', default="../train.jsonl", type=str)

    args = parser.parse_args()

    f1 = do_eval_core(gold=parse_data(args.gold), preds=parse_data(args.predict))

    print(f1)
