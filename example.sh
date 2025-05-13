#!/bin/bash

# デフォルト設定で実行
python main.py product

# カスタム入力ディレクトリを指定
python main.py product --input-dir my_images

# カスタム出力ディレクトリを指定
python main.py product --output-dir results

# 白背景透過モードを指定
python main.py product --mode white

# すべての設定をカスタマイズ
python main.py product --input-dir my_images --output-dir results --mode white