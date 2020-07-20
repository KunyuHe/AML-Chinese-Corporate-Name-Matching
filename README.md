# Chinese Corporate Name Fuzzy Matching

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9be60533ac1e459fa8c5b5dd013b4930)](https://app.codacy.com/manual/kunyuhe/AML-Chinese-Corporate-Name-Fuzzy-Matching?utm_source=github.com&utm_medium=referral&utm_content=KunyuHe/AML-Chinese-Corporate-Name-Fuzzy-Matching&utm_campaign=Badge_Grade_Dashboard) [![Maintainability](https://api.codeclimate.com/v1/badges/9fb9bc71fa28a33d7937/maintainability)](https://codeclimate.com/github/KunyuHe/AML-Chinese-Corporate-Name-Fuzzy-Matching/maintainability)

We would like to solve the business problem of screening our client list with monthly-released lists of suspected money laundering organizations and find out if any of our clients are listed. The algorithm should not be prone to data input error and intentional disguise. 

This project presents a tool that extracts the core segments of Chinese corporate names and computes the similarity between those as a weighted sum of their phonetic (sound) and glyphic (shape) similarities, implemented to help the Anti Money Laundering (AML) efforts at the bank.

- String Segmentation: utilizes the package `jieba` with user defined dictionaries and tagging.

- Fuzzy Matching:
  - Phonetic Similarity: based on the methods proposed in the [paper](https://www.aclweb.org/anthology/K18-1043/) implemented in the `DimSim` package.

    >  Min Li, Marina Danilevsky, Sara Noeman and Yunyao Li. *DIMSIM: An Accurate Chinese Phonetic Similarity Algorithm based on Learned High Dimensional Encoding*. CoNLL 2018.

    Since it only returns pairwise distance between two same-length strings in Chinese, we make use of a sliding window, take the minimum pairwise distance, and add penalty for the difference in length. To convert the distance on `[0, Inf)` to a similarity measure on `[0, 1]`, we use:

    <img src="https://render.githubusercontent.com/render/math?math=\text{similarity}=\frac{\text{arctan}(\text{dist})}{\frac{\pi}{2}}">

  - Glyphic Similarity: To compare the glyphic features of Chinese strings, we make use of the `fuzzychinese` package. It extracts the radicals (部首) and strokes (笔画), sub-character structures of each Chinese character, constructs the `tf-idf` vector for the ngram model, and computes the Cosine similarity.

## Getting Started

Follow the instructions to get a copy of the project up and running on your local machine for development and testing purposes.

First, install `Git` and navigate to a location on your machine to put this project, and run:

```consle
git clone https://github.com/KunyuHe/AML-Chinese-Corporate-Name-Fuzzy-Matching.git
cd AML-Chinese-Corporate-Name-Fuzzy-Matching
```

Install `Python` and `pip` first. After that, you can create a virtual environment and install the dependencies listed in [requirements.txt](./requirements.txt) through:

```console
pip install --user --upgrade pip
pip install --user virtualenv
venv env
.\env\Scripts\activate # For Windows, for macOS and Linux run source env/bin/activate
pip install -r requirements.txt
```

## Usage

To run the program, first put the clients list and target list (must be `.xlsx` files) under the `./data/raw/` directory. Configure the file and column names in `./config/config.yaml` accordingly.

The program uses package `jieba` for string segmentation before it performs fuzzy matching. To better extract the core segments from full corporate names, it's recommended to define and tag vocabularies for `jieba`. You can save user defined dictionaries as `.txt` files under `./data/user_dicts/` and configure `./config/config.yaml` accordingly. A example:

```txt
合伙企业 corp
有限合伙 corp
有限公司 corp
资本管理 corp
投资管理 corp
财富管理 corp
基金管理 corp
资产管理 corp
```

Run the program with:

```console
python run.py
```

You can check the available arguments with `python run.py --help`. As the matcher would use saved models to calculate glyphic similarities by default, it's important to set `--update=True` when the client list is updated.

As the output of the program, an automatically generated report of clients that have similarity scores above the threshold with at least one of the suspected money launderers for human inspection can be found under `./reports/`. A preview would also pop up in your browser as follows:

#TODO 

To fine tune the tool and configure the hyperparameters for the fuzzy matching process, again, adjust the settings in `./config/config.yaml`.

## License

This project is released under [GNU General Public License v3.0](./LICENSE).