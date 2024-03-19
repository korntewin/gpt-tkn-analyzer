# Project Overview: GPT Tokenizer Analysis
## Objective: 
To quantify the language bias within the GPT tokenizer `cl100k-base`, particularly focusing on its distribution of tokens across different languages.

## Background: 
The GPT tokenizer, particularly known for its bias towards English text, owes this inclination to the extensive amount of English documents encountered during the training of the *Byte Pair Encoding (BPE) tokenizer*. This project is dedicated to analyzing and presenting concrete data that illustrates the extent of this bias.

The GPT Tokenizer, specifically the `cl100k-base` tokenizer, comprises approximately 100,256 tokens (excluding special tokens). When a prompt is submitted to OpenAI's GPT, the following steps occur behind the scenes:

1. The prompt is tokenized into token IDs by the tokenizer.
2. OpenAI's GPT predicts the token IDs in response.
3. These token IDs are then converted back into text using the same tokenizer, and this text is returned to us.

Typically, a single word is mapped to a single token. For example:
* `token_id=100255` corresponds to the word `Conveyor`.
* `token_id=67774` corresponds to the word `Scrollbar`.

However, this behavior is not consistent across all languages. For instance:
* `token_id=70967` represents a single Thai character, `ใ`.
* `token_id=84681` also represents a single Thai character, `อ`.

This means that OpenAI's GPT requires significantly more tokens to generate a Thai paragraph!

> The *BPE* method has an advantage in encoding multilingual datasets, where tokens are generated automatically from the data based on the frequency of characters. However, this methodology comes with a penalty for low-resource languages (which obviously has lower frequency of characters😱).

## Methodology: 
Utilizing the tokenizer file found at `notebooks/data/cl100k_base.tiktoken`, I meticulously dissect and decode this tokenizer to retrieve the original text associated with each token. Subsequently, the language of the words is determined based on their Unicode code range, as specified in `src/analyze_gpt_tokenizer/config.py`.

You are welcome to substitute the tokenizer file with one from a different model or expand the Unicode code range to examine the distribution across various languages!


## Findings:

| language | size | sampling of a single token | percent_ratio |
| :--: | :--: | :--: | :--: |
| en |	88,191 |	 meal,   pcb,   proficient, Wohn, syn, zo, Madame, _metadata, ordained, _push | 87.9658
| th |	57 | 	ั, ร, ไม, ต ้, ง ื่, ท ื, ล	| 0.0569
| jp |	985 |	描述, 県, キ, 藏, 最, 后, 作, 第, 设置, 结	| 0.9825

From the summary table:

* **English Text Tokens**: An overwhelming 87.97% of tokens are allocated for English text, underscoring a significant bias towards the English language, where a **single token can often represent an entire word**.
* **Thai Text Tokens**: Conversely, only 0.06% of tokens are designated for Thai text, reflecting a considerable underrepresentation. Typically, a single token represents at most 2-3 characters, but more commonly just a single character.
* **Japanese Text Tokens**: Japanese text is slightly better represented, with 0.98% of tokens, yet it still exhibits a noticeable imbalance.

> To reiterate, the total number of tokens (vocabulary size) is 100,256 (excluding special tokens), indicating that the vast majority of tokens cater to English text.


## Conclusion: 
The analysis confirms a heavy bias in the GPT tokenizer towards English, with other languages like Thai and Japanese being significantly underrepresented. This insight could be pivotal for future developments in tokenizer technology to create a more balanced linguistic representation.

# Visualization
The rank of a token is determined during the BPE (Byte Pair Encoding) merging phase, where the most common pairs of tokens are merged incrementally generating a new rank. This means that tokens with a higher rank always have a longer text length, and thus, typically form more meaningful words.

By generating a wordcloud sorted by rank and grouped by language, we can observe the themes of the longest possible *texts per token* in various languages.

From the word cloud below, it is clear that the longest text in the Thai token is `การ`, which is not a meaningful word at all 😂. This results in GPT needing to compose multiple tokens to form a single word, and many more tokens to form a paragraph! In contrast, with English tokens, a single token often represents a meaningful word, such as `conveyor`, `daycare`, or `merciless`.

> The image below represent the wordcloud of each token on different language!

## English
<img src="pics/en_wordcloud.jpg.png" width="auto">

## Thai
<img src="pics/th_wordcloud.jpg.png" width="auto">

## Japanese
<img src="pics/jp_wordcloud.jpg.png" width="auto">

# Set up

To reproduce this project on your local machine, I recommend to use [rye](https://rye-up.com/) as a package and also a python version management tool. Personally recommended to use `uv` as package installer for `rye` for blazingly fast package resolving & installing using Rust!

After you have `rye` installed:

1. Run `rye sync --no-lock` to generate `.venv` in your directory. And if you didn't already have `python 3.12`, rye will also set that up for you.
2. Run `rye run analyze-gpt-tokenizer` to generate `summary.csv` and `token_text.csv` for further analysis!
3. You can also check additional params by running `rye run analyze-gpt-tokenizer --help`

# Project structure

```tree
├── README.md
├── notebooks  # For interative analysis
│   ├── analyze.ipynb
│   ├── data
│   │   └── cl100k_base.tiktoken
│   ├── fonts
│   │   ├── *.ttf
│   └── output
│       ├── cl100k_base.text.csv
│       └── cl100k_base.token_summary.csv
├── pyproject.toml
├── requirements-dev.lock
├── requirements.lock
└── src  # Command line source code
    └── analyze_gpt_tokenizer
        ├── __init__.py
        ├── __main__.py
        ├── _types.py
        ├── config.py
        └── utils.py
```