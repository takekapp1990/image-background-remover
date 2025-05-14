#!/bin/bash

# 基本的な実行例
echo "=== 基本的な実行例 ==="
python main.py my_prefix  # デフォルト設定で実行

# プレフィックスのみ指定
echo -e "\n=== プレフィックスのみ指定 ==="
python main.py my_prefix  # プレフィックスを指定して実行

# 入力ディレクトリの指定
echo -e "\n=== 入力ディレクトリの指定 ==="
python main.py my_prefix --input-dir ~/Downloads/my_images/  # カスタム入力ディレクトリを指定

# 出力ディレクトリの指定
echo -e "\n=== 出力ディレクトリの指定 ==="
python main.py my_prefix --output-dir ~/Downloads/my_images/png  # カスタム出力ディレクトリを指定

# 背景削除モードの指定
echo -e "\n=== 背景削除モードの指定 ==="
python main.py my_prefix --mode rembg  # AIによる背景削除
python main.py my_prefix --mode auto   # 背景色自動検出

# すべての設定をカスタマイズ
echo -e "\n=== すべての設定をカスタマイズ ==="
python main.py my_prefix --input-dir ~/Downloads/my_images/ --output-dir ~/Downloads/my_images/png --mode auto

# 異なるモードでの比較
echo -e "\n=== 異なるモードでの比較 ==="
python main.py my_prefix --input-dir ~/Downloads/my_images/ --output-dir ~/Downloads/my_images/rembg --mode rembg
python main.py my_prefix --input-dir ~/Downloads/my_images/ --output-dir ~/Downloads/my_images/auto --mode auto