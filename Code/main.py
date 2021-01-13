import argparse
import pickle
import time
from pathlib import Path
from sys import stdin, stderr, path

project_dir = Path(__file__).parent.resolve()
if str(project_dir) not in path:
    path.append(str(project_dir))
if str(project_dir / 'src') not in path:
    path.append(str(project_dir / 'src'))

from check import PlagiarismChecker
from make_index import Index
from tabulate import tabulate

THRESHOLD = 0.3


def gen_index(args):
    p = Path(args.index)
    if not p.is_dir():
        print("Index path must be a directory containing the corpus files!", file=stderr)
        exit(1)
    index = Index()
    for file in p.iterdir():
        if not file.is_file():
            continue
        contents = file.read_text(encoding='unicode_escape')
        index.add_doc(file, contents)
    index.normalize_docs()
    with open('index.pk', 'wb+') as f:
        pickle.dump(index, f)
    print('Index generated in index.pk')


def check_for_plagiarism(args):
    contents = {}
    if args.file == '-':
        contents['stdin'] = stdin.read()
    else:
        p = Path(args.file)
        if p.is_file():
            contents[p] = p.read_text(encoding='unicode_escape')
        elif p.is_dir():
            for file in p.iterdir():
                if not file.is_file():
                    continue
                contents[file] = file.read_text(encoding='unicode_escape')
    with open('index.pk', 'rb') as f:
        index = pickle.load(f)
    checker = PlagiarismChecker(index)
    data = {}
    for file, contents in contents.items():
        scores = checker.find_score(contents)
        data[file] = sorted([(original, score) for original, score in scores.items() if score > THRESHOLD],
                            reverse=True, key=lambda x: x[1])
    tabulate(data)


def main():
    parser = argparse.ArgumentParser(description='Check for plagiarism in your documents')
    commands = parser.add_subparsers(required=True)

    query = commands.add_parser('query', help='Check file for plagiarism')
    query.add_argument('file', type=str, help='Check this file (or all files in this folder)')
    query.set_defaults(func=check_for_plagiarism)

    index = commands.add_parser('index', help='Make index')
    index.add_argument('index', type=str, help='Index this directory')
    index.set_defaults(func=gen_index)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("Execution Time = ", time.time() - start_time)
