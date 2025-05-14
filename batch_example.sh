#!/bin/bash

# 入力ディレクトリと出力ディレクトリの設定
INPUT_DIR="input"
OUTPUT_DIR="output"

# 出力ディレクトリが存在しない場合は作成
mkdir -p "$OUTPUT_DIR"

# 基本的な使用方法
echo "基本的な使用方法:"
python main.py

# プレフィックスを指定する場合
echo -e "\nプレフィックスを指定する場合:"
python main.py --prefix "processed_"

# 入力ディレクトリを指定する場合
echo -e "\n入力ディレクトリを指定する場合:"
python main.py --input-dir "my_images"

# 出力ディレクトリを指定する場合
echo -e "\n出力ディレクトリを指定する場合:"
python main.py --output-dir "processed"

# 出力サイズを指定する場合
echo -e "\n出力サイズを指定する場合:"
python main.py --output-size 800 800

# 異なるモードで処理を比較する場合
echo -e "\n異なるモードで処理を比較する場合:"
# rembgモード
python main.py --mode rembg --prefix "rembg_"
# autoモード
python main.py --mode auto --prefix "auto_"

# 異なる出力サイズで処理を比較する場合
echo -e "\n異なる出力サイズで処理を比較する場合:"
# 小さいサイズ
python main.py --output-size 400 400 --prefix "small_"
# 大きいサイズ
python main.py --output-size 1200 1200 --prefix "large_"

# カスタム設定を組み合わせる場合
echo -e "\nカスタム設定を組み合わせる場合:"
python main.py --input-dir "my_images" --output-dir "processed" --prefix "custom_" --output-size 800 800
