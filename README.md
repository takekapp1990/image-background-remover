# 画像背景削除ツール

画像の背景を自動で削除し、前景を中央に配置してリサイズするPythonツールです。

## 機能

- 画像の背景を自動で削除
- 前景を中央に配置
- 前景を適切なサイズにリサイズ（デフォルトで90%）
- ファイル名の正規化（英数字のみ、スペースをアンダースコアに変換）

## 必要条件

- Python 3.7以上
- 以下のPythonパッケージ:
  - rembg
  - Pillow (PIL)

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

1. `input`ディレクトリを作成し、処理したい画像を配置します
2. 以下のコマンドを実行:
```bash
python main.py <prefix>
```

例:
```bash
python main.py product
```

### 引数

- `prefix`: 出力ファイル名のプレフィックス（例: product_1_image.png）

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