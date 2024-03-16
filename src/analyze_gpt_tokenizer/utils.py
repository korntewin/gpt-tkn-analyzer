from collections import Counter

import pandas as pd

from ._types import CHAR_RANKS
from .config import CODE_RANGES


def detect_lang(
    c: str, rangess: dict[str, tuple[tuple[str, str]]] = CODE_RANGES
) -> str:
    for lang, ranges in rangess.items():
        for _range in ranges:
            if _range[0] <= c <= _range[1]:
                return lang

    return "UNK"


def extract_line(pair) -> tuple[str, str, str]:
    rank, text = pair
    commons = Counter([detect_lang(c) for c in text]).most_common(1)

    lang = commons[0][0]

    return text, lang, rank


def get_tokens_from_lang(lang: str, char_ranks: CHAR_RANKS) -> list[str]:
    return list(filter(lambda t: t[1] == lang, char_ranks))


def get_num_tokens_from_lang(lang: str, char_ranks: CHAR_RANKS) -> int:
    return len(get_tokens_from_lang(lang, char_ranks))


def get_summary_table(
    char_ranks: CHAR_RANKS, rangess: dict[str, tuple[tuple[str, str]]] = CODE_RANGES
) -> pd.DataFrame:
    output = []
    for lang in rangess.keys():
        tokens = get_tokens_from_lang(lang, char_ranks)
        size = len(tokens)
        sampling = "  ".join(
            pd.DataFrame(tokens)
            .sample(min(10, size), random_state=987)
            .iloc[:, 0]
            .to_list()
        )
        output.append((lang, size, sampling))

    return pd.DataFrame(output, columns=["lang", "size", "sampling"]).assign(
        percent_ratio=lambda x: (x["size"] / x["size"].sum() * 100).round(4)
    )
