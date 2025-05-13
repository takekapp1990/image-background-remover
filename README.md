# 画像背景削除ツール

画像の背景を自動で削除し、前景を中央に配置してリサイズするPythonツールです。

## 機能

- 画像の背景を自動で削除
  - AIによる背景削除（rembg）
  - 白背景透過モード
- 前景を中央に配置
- 前景を適切なサイズにリサイズ（デフォルトで90%）
- ファイル名の正規化（英数字のみ、スペースをアンダースコアに変換）
- カスタマイズ可能な入出力ディレクトリ
- コマンドライン引数による設定のカスタマイズ

## 必要条件

- Python 3.7以上
- 以下のPythonパッケージ:
  - rembg
  - Pillow (PIL)
  - numpy

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/image_rembg.git
cd image_rembg
```

2. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 入力ディレクトリを作成し、処理したい画像を配置します
   - デフォルトでは`input`ディレクトリを使用
   - `--input-dir`オプションで変更可能

2. 以下のコマンドを実行:
```bash
python main.py <prefix> [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR] [--mode {rembg,white}]
```

例:
```bash
# デフォルト設定で実行
python main.py product

# カスタム設定で実行
python main.py product --input-dir my_images --output-dir results --mode white
```

### 引数

- `prefix`: 出力ファイル名のプレフィックス（必須）
- `--input-dir`: 入力ディレクトリのパス（オプション）
- `--output-dir`: 出力ディレクトリのパス（オプション）
- `--mode`: 背景削除モード（rembg または white）（オプション）

### デフォルト設定

以下の設定は`main.py`内の定数で定義されており、コマンドライン引数で上書きできます：

- 入力ディレクトリ: `"input"`
- 出力ディレクトリ: `"output"`
- 背景削除モード: `"rembg"`

### 背景削除モード

ツールは2つの背景削除モードをサポートしています：

1. AIによる背景削除（デフォルト）
   - 複雑な背景でも高精度に前景を抽出
   - 髪の毛などの半透明な部分も適切に処理

2. 白背景透過モード
   - 白い背景を持つ画像に最適化
   - 高速な処理が可能
   - 白と判断する閾値を調整可能（デフォルト: 240）

モードの切り替えは`main.py`内の`BACKGROUND_REMOVAL_MODE`定数で設定：
- `"rembg"`: AIによる背景削除（デフォルト）
- `"white"`: 白背景透過

### 対応画像形式

- PNG
- JPG/JPEG

## 出力

- 処理された画像は`output`ディレクトリに保存されます
- 出力ファイル名の形式: `<prefix>_<number>_<original_name>.png`

## エラーメッセージ

ツールは以下のような状況でエラーメッセージを表示します：

- 引数が不正な場合
- `input`ディレクトリが存在しない場合
- 処理可能な画像が見つからない場合
- 画像処理中にエラーが発生した場合

## ライセンス

MITライセンス

## 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成 