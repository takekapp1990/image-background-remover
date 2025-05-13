"""
画像の背景を削除し、前景を中央に配置してリサイズするツール

使用方法:
    python main.py <prefix>

引数:
    prefix: 出力ファイル名のプレフィックス

機能:
    - 画像の背景を自動で削除
    - 前景を中央に配置
    - 前景を適切なサイズにリサイズ（デフォルトで90%）
    - ファイル名の正規化（英数字のみ、スペースをアンダースコアに変換）
"""

from rembg import remove
from PIL import Image
import os
import sys
import re
import io
import shutil

# 背景削除の設定
DEFAULT_MARGIN_RATIO = 0.1  # 10%余白（前景を90%にスケーリング）

# rembgの背景削除パラメータ
ALPHA_MATTING = False  # アルファマット処理の有効/無効
# True: 半透明な部分（髪の毛など）の処理が改善されるが、処理時間が長くなる
# False: 通常の背景削除処理（デフォルト）

ALPHA_MATTING_FOREGROUND_THRESHOLD = 240  # 前景と判断する閾値（0-255）
# 値が大きいほど前景として認識されやすくなる
# 240: ほぼ白に近い部分を前景として認識（デフォルト）

ALPHA_MATTING_BACKGROUND_THRESHOLD = 10  # 背景と判断する閾値（0-255）
# 値が小さいほど背景として認識されやすくなる
# 10: ほぼ黒に近い部分を背景として認識（デフォルト）

ALPHA_MATTING_ERODE_SIZE = 10  # エロード処理のサイズ
# 値が大きいほど境界が滑らかになる
# 10: 中程度の滑らかさ（デフォルト）
# 0: エロード処理なし
# 20以上: より滑らかな境界

POST_PROCESS_MASK = True  # 後処理マスクの有効/無効
# True: エッジの処理を改善し、より自然な境界を作成（デフォルト）
# False: 後処理を行わない（処理が速くなるが、境界が粗くなる可能性がある）

def validate_input():
    """コマンドライン引数の検証"""
    if len(sys.argv) != 2:
        print("エラー: 引数が不正です")
        print("使用方法: python main.py <prefix>")
        print("例: python main.py product")
        sys.exit(1)

    if not os.path.exists('input'):
        print("エラー: 'input'ディレクトリが見つかりません")
        print("'input'ディレクトリを作成し、処理したい画像を配置してください")
        sys.exit(1)

    if not any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in os.listdir('input')):
        print("エラー: 'input'ディレクトリに画像ファイルが見つかりません")
        print("対応形式: .png, .jpg, .jpeg")
        sys.exit(1)

def sanitize_filename(filename):
    """
    ファイル名を正規化する
    
    Args:
        filename: 元のファイル名
        
    Returns:
        正規化されたファイル名（英数字のみ、スペースをアンダースコアに変換）
    """
    name, _ = os.path.splitext(filename)
    name = re.sub(r'[^\x00-\x7F]', '', name)
    name = name.replace(' ', '_').lower()
    return name

def get_foreground_bbox(image: Image.Image):
    """
    前景画像の境界ボックスを取得する
    
    Args:
        image: PIL Imageオブジェクト
        
    Returns:
        前景画像の境界ボックス (left, upper, right, lower)
    """
    alpha = image.split()[-1]
    bbox = alpha.getbbox()
    return bbox

def scale_foreground(image: Image.Image, margin_ratio=DEFAULT_MARGIN_RATIO):
    """
    前景画像をスケーリングして中央に配置する
    
    Args:
        image: PIL Imageオブジェクト
        margin_ratio: 余白の比率（デフォルト: 0.1 = 10%）
        
    Returns:
        スケーリングされた画像
    """
    orig_w, orig_h = image.size
    bbox = get_foreground_bbox(image)

    if bbox is None:
        print("警告: 前景が見つかりませんでした。画像をそのまま保存します。")
        return image

    # 前景画像をトリミング
    fg = image.crop(bbox)
    fg_w, fg_h = fg.size

    # スケーリング比率を計算（長辺基準）
    target_ratio = 1.0 - margin_ratio
    scale_w = (orig_w * target_ratio) / fg_w
    scale_h = (orig_h * target_ratio) / fg_h
    scale = min(scale_w, scale_h)  # はみ出ないように小さい方を採用

    new_w = int(fg_w * scale)
    new_h = int(fg_h * scale)

    # リサイズ後の画像を中央に貼り付け
    fg_resized = fg.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (orig_w, orig_h), (0, 0, 0, 0))

    offset_x = (orig_w - new_w) // 2
    offset_y = (orig_h - new_h) // 2
    canvas.paste(fg_resized, (offset_x, offset_y), fg_resized)

    return canvas

def main():
    """メイン処理"""
    validate_input()
    prefix = sys.argv[1]

    input_dir = 'input'
    output_dir = 'output'

    if os.path.exists(output_dir):
        # .gitkeepファイルを一時的に保存
        gitkeep_path = os.path.join(output_dir, '.gitkeep')
        has_gitkeep = os.path.exists(gitkeep_path)
        if has_gitkeep:
            with open(gitkeep_path, 'rb') as f:
                gitkeep_content = f.read()
        
        # 出力ディレクトリを削除
        shutil.rmtree(output_dir)
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # .gitkeepファイルを復元
    if has_gitkeep:
        with open(gitkeep_path, 'wb') as f:
            f.write(gitkeep_content)

    counter = 1
    processed_count = 0

    for filename in sorted(os.listdir(input_dir)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                input_path = os.path.join(input_dir, filename)

                base_name = sanitize_filename(filename)
                output_name = f"{prefix}_{counter}_{base_name}.png"
                output_path = os.path.join(output_dir, output_name)

                with open(input_path, 'rb') as i:
                    input_data = i.read()
                    output_data = remove(
                        input_data,
                        alpha_matting=ALPHA_MATTING,
                        alpha_matting_foreground_threshold=ALPHA_MATTING_FOREGROUND_THRESHOLD,
                        alpha_matting_background_threshold=ALPHA_MATTING_BACKGROUND_THRESHOLD,
                        alpha_matting_erode_size=ALPHA_MATTING_ERODE_SIZE,
                        post_process_mask=POST_PROCESS_MASK
                    )

                    image = Image.open(io.BytesIO(output_data)).convert("RGBA")
                    centered_scaled = scale_foreground(image)
                    centered_scaled.save(output_path)

                print(f"処理完了: {filename} → {output_name}")
                counter += 1
                processed_count += 1
            except Exception as e:
                print(f"エラー: {filename}の処理中にエラーが発生しました")
                print(f"エラー内容: {str(e)}")

    if processed_count == 0:
        print("エラー: 処理可能な画像が見つかりませんでした")
        sys.exit(1)
    else:
        print(f"\n処理完了: {processed_count}個の画像を処理しました")
        print(f"出力先: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()

