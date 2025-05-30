#!/bin/bash
cd "$(dirname "$0")"

python ./crawler/arxiv_rss_parser.py
python ./crawler/github_trends.py
python ./crawler/qbitai_rss_parser.py
python ./crawler/news/36kr.py
python ./crawler/news/leiphone.py
# python ./crawler/tweet.py
