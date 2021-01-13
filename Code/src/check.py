from pathlib import Path
from typing import Dict

from utils import tokenize, normalize
from make_index import Index


class PlagiarismChecker:
    """
    Checks files for plagiarism w.r.t to the index given during initialization
    """

    def __init__(self, index: Index):
        self.index = index

    def find_score(self, contents: str) -> Dict[Path, float]:
        """
        Check file contents for plagiarism
        :param contents: The file contents to check for plagiarism
        :return: Dictionary of plagiarism score w.r.t each original document
        """
        score_list = {}
        tokens = normalize(tokenize(contents), self.index.doc_freq)
        for document, tf_map in self.index.term_freqs.items():
            score = sum(tf_idf * tf_map[token] for token, tf_idf in tokens.items() if token in tf_map)
            score_list[document] = score
        return score_list
