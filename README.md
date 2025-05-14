# 画像背景削除ツール

このツールは、画像の背景を自動で削除し、前景を中央に配置してリサイズするPythonスクリプトです。

## 機能

- 画像の背景を自動で削除
  - AIによる背景削除（rembg）
  - 画像の端から背景色を自動検出して削除（auto）
- 前景を中央に配置
- 前景を適切なサイズにリサイズ（デフォルトで90%）
- ファイル名の正規化（英数字のみ、スペースをアンダースコアに変換）
- カスタマイズ可能な入出力ディレクトリ
- コマンドライン引数による設定のカスタマイズ

## 必要条件

- Python 3.8以上
- 以下のPythonパッケージ:
  - rembg
  - Pillow (PIL)
  - numpy

## インストール

1. リポジトリをクローンまたはダウンロード:
```bash
git clone https://github.com/yourusername/image_rembg.git
cd image_rembg
```

2. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 入力画像を`input`ディレクトリに配置
2. スクリプトを実行:
```bash
python main.py [プレフィックス] [オプション]
```

### オプション

- `--input-dir`: 入力ディレクトリのパス（デフォルト: `input`）
- `--output-dir`: 出力ディレクトリのパス（デフォルト: `output`）
- `--mode`: 背景削除モード
  - `rembg`: AIによる背景削除
  - `auto`: 画像の端から背景色を自動検出して削除（デフォルト）

### 例

```bash
# デフォルト設定で実行
python main.py

# カスタムプレフィックスと入力/出力ディレクトリを指定
python main.py my_prefix --input-dir custom_input --output-dir custom_output

# 背景削除モードを指定
python main.py --mode rembg  # AIによる背景削除
python main.py --mode auto   # 背景色自動検出
```

### 引数

- `prefix`: 出力ファイル名のプレフィックス（オプション）
  - 省略可能（デフォルト: なし）
  - 指定した場合: `<prefix>_<number>_<original_name>.png`
  - 省略した場合: `<original_name>.png`

### デフォルト設定

以下の設定は`main.py`内の定数で定義されており、コマンドライン引数で上書きできます：

- 入力ディレクトリ: `"input"`
- 出力ディレクトリ: `"output"`
- 背景削除モード: `"rembg"`
- プレフィックス: `""`（なし）

### 背景削除モード

ツールは2つの背景削除モードをサポートしています：

1. AIによる背景削除（デフォルト）
   - 複雑な背景でも高精度に前景を抽出
   - 髪の毛などの半透明な部分も適切に処理

2. 画像の端から背景色を自動検出して削除
   - 背景色と判断する色の差の閾値を調整可能（デフォルト: 240）
   - 端からのサンプリング範囲を調整可能（デフォルト: 100）

モードの切り替えは`main.py`内の`BACKGROUND_REMOVAL_MODE`定数で設定：
- `"rembg"`: AIによる背景削除（デフォルト）
- `"auto"`: 画像の端から背景色を自動検出して削除

### 対応画像形式

- PNG
- JPG/JPEG

## 出力

処理済みの画像は`output`ディレクトリ（または指定した出力ディレクトリ）に保存されます。
ファイル名は以下の形式で生成されます：
`[プレフィックス]_[元のファイル名（正規化済み）].png`

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