import json
import random

from os.path import dirname, realpath, join


current_dir = dirname(realpath(__file__))
DATA_DIR = join(current_dir, "../")


def get_random_span(text):
    text_length = len(text)
    start = random.randint(0, text_length - 1)
    end = random.randint(start, text_length)

    while text[end-1] == ' ' and end > start:
        end -= 1

    while text[start] == ' ' and start < end:
        start += 1

    while end < len(text):
        if text[end] == ' ':
            break
        end += 1

    while start > 0:
        if text[start-1] == ' ':
            break
        start -= 1

    return text[start:end], f"{start}:{end}"


def random_opinion(text, polarities=["POS", "NEG"]):
    ta, a = get_random_span(text)
    tb, b = get_random_span(text)
    tc, c = get_random_span(text)

    assert(not ta.startswith(' '))
    assert(not tb.startswith(' '))
    assert(not tc.startswith(' '))

    assert(not ta.endswith(' '))
    assert(not tb.endswith(' '))
    assert(not tc.endswith(' '))

    return {
        "Source": [[ta], [a]],
        "Target": [[tb], [b]],
        "Polar_expression": [[tc], [c]],
        "Polarity": random.choice(polarities),
    }


def extent_n_times(lst, n):
    if n > 0:
        r = []
        for _ in range(n):
            r.extend(lst)
        return r
    else:
        return lst


def create_submission(load_data_func, ops_max_count=3, duplicate_times=0, **kwargs):
    sentences = load_data_func()
    for sentence in sentences:

        registered_opinions = set()

        # create.
        opinions = []
        for _ in range(random.randint(0, ops_max_count)):
            opinion = random_opinion(sentence["text"], **kwargs)

            # Create opinion key that combines: Source, Target, Polarity.
            opinion_key = "-".join(list(opinion["Source"][1]) +
                                   list(opinion["Target"][1]) +
                                   [opinion["Polarity"]])

            if opinion_key not in registered_opinions:
                opinions.append(opinion)
            registered_opinions.add(opinion_key)

        # optionally duplicate.
        opinions = extent_n_times(lst=opinions, n=duplicate_times)
        # save.
        sentence["opinions"] = opinions

    return sentences


def to_jsonl(data, target):
    with open(target, "w") as f:
        for item in data:
            f.write(f"{json.dumps(item, ensure_ascii=False)}\n")
