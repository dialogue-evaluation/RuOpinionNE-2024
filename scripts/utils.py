import os
import zipfile


def spreadsheet_format_line(args_list, new_line=True):
    return "\t".join([str(v) for v in args_list]) + "\n" if new_line else ""


def dict_try_get(d, path, default=None):
    for p in path:
        if p in d:
            d = d[p]
        else:
            return default
    return d


def dict_dfs_traversal(d, path=None):
    if path is None:
        path = []

    if isinstance(d, dict):
        for key, value in d.items():
            new_path = path + [key]
            yield from dict_dfs_traversal(value, new_path)
    else:
        yield path, d


def dict_register_path(d, path, value_if_not_exist=None):
    # register path.
    target = d
    for p in path[:-1]:
        if p not in target:
            target[p] = dict()
        target = target[p]

    # register value only if the latter is not presented.
    if path[-1] not in target:
        target[path[-1]] = value_if_not_exist

    # Returning the value that is related to the provided path.
    return target[path[-1]]


def iter_dir_filepaths(from_dir, filter_full_path=None):
    assert (isinstance(from_dir, str))

    for root, _, files in os.walk(from_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if filter_full_path is not None:
                if not filter_full_path(full_path):
                    continue
            yield full_path


def iter_submission_lines(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        if len(file_list) == 1:
            file_name = file_list[0]
            with zip_ref.open(file_name) as file:
                return file.readlines()
        else:
            print("The ZIP archive does not contain exactly one file.")


def flatten(xss):
    return [x for xs in xss for x in xs]


def uppercase_substring(s, start, end):
    assert(isinstance(s, str))
    if not (0 <= start < len(s)) or not (0 <= end <= len(s)) or start > end:
        raise ValueError("Invalid start or end indices")

    return s[:start] + s[start:end].upper() + s[end:]


def bracket_substring(s, start, end) -> str:
    if not (0 <= start < len(s)) or not (0 <= end <= len(s)) or start > end:
        raise ValueError("Invalid start or end indices")

    return s[:start] + "[" + s[start:end] + "]" + s[end:]