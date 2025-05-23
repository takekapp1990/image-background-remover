"""
画像の背景を削除し、前景を中央に配置してリサイズするツール

主な機能:
    - 画像の背景を自動的に検出し、削除
    - 背景色を指定して削除
    - 境界部分の処理による自然な背景削除
    - 出力サイズのカスタマイズ
    - バッチ処理対応

使用方法:
    python main.py [オプション]

オプション:
    --input-dir: 入力ディレクトリのパス（デフォルト: "input"）
    --output-dir: 出力ディレクトリのパス（デフォルト: "output"）
    --mode: 背景削除モード（"auto" または "rembg"）（デフォルト: "auto"）
    --prefix: 出力ファイル名のプレフィックス（デフォルト: ""）
    --output-size: 出力画像のサイズ（例: "800 800"）（デフォルト: 元画像のサイズ）
"""

from rembg import remove
from PIL import Image
import os
import sys
import re
import io
import shutil
import numpy as np
import argparse
from typing import Tuple

# デフォルト設定
DEFAULT_INPUT_DIR = "input"  # 入力画像を配置するディレクトリ
DEFAULT_OUTPUT_DIR = "output"  # 処理済み画像を保存するディレクトリ
DEFAULT_BACKGROUND_REMOVAL_MODE = "auto"  # 背景削除モード（"auto" または "rembg"）
DEFAULT_PREFIX = ""  # デフォルトのプレフィックス（空文字）
DEFAULT_OUTPUT_SIZE = None  # デフォルトの出力サイズ（Noneの場合は元画像のサイズを使用）

# 背景削除の設定
DEFAULT_MARGIN_RATIO = 0.1  # 10%余白（前景を90%にスケーリング）

# 背景色検出の設定
EDGE_SAMPLE_SIZE = 5  # 端から何ピクセル分をサンプリングするか
COLOR_THRESHOLD = 5  # 背景色と判断する色の差の閾値
# 値が小さいほど厳密な判定になります
# 5: 厳密な判定（推奨）
# 10: 中程度の判定
# 20以上: 緩い判定

# 境界処理の設定
BOUNDARY_DILATION_SIZE = 10  # 境界部分の拡張範囲（ピクセル数）
BOUNDARY_COLOR_THRESHOLD = 10  # 境界部分の色の類似度判定の閾値
# 値が大きいほど境界部分の色の判定が緩くなります
# 5: 厳密な判定（背景色に近い色のみ透過）
# 10: 中程度の判定（推奨）
# 20以上: 緩い判定（より広い範囲の色を透過）

# 白背景透過の設定
WHITE_THRESHOLD = 240  # 白と判断する閾値（0-255）
# 値が大きいほど白として認識されやすくなる
# 240: ほぼ白に近い部分を背景として認識

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

def parse_arguments():
    """
    コマンドライン引数の解析
    
    Returns:
        tuple: (prefix, input_dir, output_dir, mode, output_size)
            - prefix: 出力ファイル名のプレフィックス
            - input_dir: 入力ディレクトリのパス
            - output_dir: 出力ディレクトリのパス
            - mode: 背景削除モード
            - output_size: 出力画像のサイズ (width, height)
    """
    parser = argparse.ArgumentParser(description='画像の背景を削除し、前景を中央に配置するツール')
    parser.add_argument('prefix', nargs='?', default=DEFAULT_PREFIX, help='出力ファイル名のプレフィックス（省略可）')
    parser.add_argument('--input-dir', help='入力ディレクトリのパス')
    parser.add_argument('--output-dir', help='出力ディレクトリのパス')
    parser.add_argument('--mode', choices=['rembg', 'auto'], help='背景削除モード（rembg または auto）')
    parser.add_argument('--output-size', type=int, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                      help='出力画像のサイズ（幅 高さ）')
    
    args = parser.parse_args()
    
    # デフォルト値の設定
    input_dir = args.input_dir if args.input_dir else DEFAULT_INPUT_DIR
    output_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_DIR
    mode = args.mode if args.mode else DEFAULT_BACKGROUND_REMOVAL_MODE
    prefix = args.prefix if args.prefix else DEFAULT_PREFIX
    output_size = tuple(args.output_size) if args.output_size else DEFAULT_OUTPUT_SIZE
    
    return prefix, input_dir, output_dir, mode, output_size

def validate_input(input_dir):
    """
    入力ディレクトリの検証
    
    Args:
        input_dir: 入力ディレクトリのパス
        
    Raises:
        SystemExit: 入力ディレクトリが存在しない、または画像ファイルが見つからない場合
    """
    if not os.path.exists(input_dir):
        print(f"エラー: '{input_dir}'ディレクトリが見つかりません")
        print(f"'{input_dir}'ディレクトリを作成し、処理したい画像を配置してください")
        sys.exit(1)

    if not any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in os.listdir(input_dir)):
        print(f"エラー: '{input_dir}'ディレクトリに画像ファイルが見つかりません")
        print("対応形式: .png, .jpg, .jpeg")
        sys.exit(1)

def sanitize_filename(filename):
    """
    ファイル名を正規化する
    
    Args:
        filename: 元のファイル名
        
    Returns:
        str: 正規化されたファイル名（英数字のみ、スペースをアンダースコアに変換）
    """
    name, _ = os.path.splitext(filename)
    name = re.sub(r'[^\x00-\x7F]', '', name)  # 非ASCII文字を削除
    name = name.replace(' ', '_').lower()  # スペースをアンダースコアに変換し、小文字化
    return name

def get_foreground_bbox(image: Image.Image):
    """
    前景画像の境界ボックスを取得する
    
    Args:
        image: PIL Imageオブジェクト
        
    Returns:
        tuple: 前景画像の境界ボックス (left, upper, right, lower)
            前景が見つからない場合はNone
    """
    alpha = image.split()[-1]  # アルファチャンネルを取得
    bbox = alpha.getbbox()  # 非透明部分の境界ボックスを取得
    return bbox

def scale_foreground(image: Image.Image, margin_ratio=DEFAULT_MARGIN_RATIO, output_size=DEFAULT_OUTPUT_SIZE):
    """
    前景画像をスケーリングして中央に配置する
    
    Args:
        image: PIL Imageオブジェクト
        margin_ratio: 余白の比率（デフォルト: 0.1 = 10%）
        output_size: 出力画像のサイズ (width, height)。Noneの場合は元画像のサイズを使用
        
    Returns:
        Image.Image: スケーリングされた画像
    """
    # 出力サイズが指定されていない場合は元画像のサイズを使用
    if output_size is None:
        output_size = image.size
    
    # 出力サイズに合わせてキャンバスを作成
    canvas = Image.new("RGBA", output_size, (0, 0, 0, 0))
    orig_w, orig_h = output_size
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
    offset_x = (orig_w - new_w) // 2
    offset_y = (orig_h - new_h) // 2
    canvas.paste(fg_resized, (offset_x, offset_y), fg_resized)

    return canvas

def remove_white_background(image: Image.Image):
    """
    白い背景を透過する
    
    Args:
        image: PIL Imageオブジェクト
        
    Returns:
        背景が透過された画像
    """
    # 画像をRGBAモードに変換
    image = image.convert("RGBA")
    data = np.array(image)
    
    # RGBの各チャンネルが閾値以上の場合を白と判断
    white_mask = np.all(data[:, :, :3] >= WHITE_THRESHOLD, axis=2)
    
    # 白い部分を透過
    data[:, :, 3] = np.where(white_mask, 0, 255)
    
    return Image.fromarray(data)

def detect_background_color(image: Image.Image) -> tuple:
    """
    画像の端から背景色を検出する
    
    Args:
        image: PIL Imageオブジェクト
        
    Returns:
        tuple: 検出された背景色 (R, G, B)
    """
    width, height = image.size
    edge_pixels = []
    
    # 画像の端からピクセルをサンプリング
    for x in range(EDGE_SAMPLE_SIZE):
        for y in range(height):
            edge_pixels.append(image.getpixel((x, y)))  # 左端
            edge_pixels.append(image.getpixel((width - 1 - x, y)))  # 右端
    
    for y in range(EDGE_SAMPLE_SIZE):
        for x in range(width):
            edge_pixels.append(image.getpixel((x, y)))  # 上端
            edge_pixels.append(image.getpixel((x, height - 1 - y)))  # 下端
    
    # 最も頻出する色を背景色として検出
    color_counts = {}
    for pixel in edge_pixels:
        if pixel in color_counts:
            color_counts[pixel] += 1
        else:
            color_counts[pixel] = 1
    
    background_color = max(color_counts.items(), key=lambda x: x[1])[0]
    return background_color

def remove_background_color(image: Image.Image, bg_color: Tuple[int, int, int]):
    """
    指定された背景色を透過する
    
    Args:
        image: PIL Imageオブジェクト
        bg_color: 背景色 (R, G, B)
        
    Returns:
        Image.Image: 背景が透過された画像
    """
    # 画像をRGBAモードに変換
    image = image.convert("RGBA")
    data = np.array(image)
    
    # 背景色との差を計算
    color_diff = np.abs(data[:, :, :3] - bg_color)
    is_background = np.all(color_diff <= COLOR_THRESHOLD, axis=2)
    
    # 背景部分を透過
    data[:, :, 3] = np.where(is_background, 0, 255)
    
    # 境界部分の検出と処理（NumPyを使用して高速化）
    height, width = data.shape[:2]
    
    # 前景ピクセルのマスクを作成
    is_foreground = ~is_background
    
    # 境界ピクセルの検出（NumPyの畳み込みを使用）
    kernel = np.ones((3, 3), dtype=bool)
    kernel[1, 1] = False  # 中心ピクセルは除外
    
    # 前景ピクセルの周囲に背景ピクセルが存在するかチェック
    foreground_padded = np.pad(is_foreground, 1, mode='constant', constant_values=False)
    boundary_mask = np.zeros_like(is_foreground)
    
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                continue
            # シフトしたマスクと元のマスクのANDを取る
            shifted = foreground_padded[i:i+height, j:j+width]
            boundary_mask |= (is_foreground & ~shifted)
    
    # 境界部分の色の類似度を計算
    color_similarity = np.mean(color_diff, axis=2)
    boundary_color_mask = color_similarity <= BOUNDARY_COLOR_THRESHOLD
    
    # 境界部分の拡張（NumPyの畳み込みを使用）
    if BOUNDARY_DILATION_SIZE > 0:
        dilation_kernel = np.ones((2*BOUNDARY_DILATION_SIZE+1, 2*BOUNDARY_DILATION_SIZE+1), dtype=bool)
        boundary_mask = np.pad(boundary_mask, BOUNDARY_DILATION_SIZE, mode='constant', constant_values=False)
        boundary_mask = np.maximum.reduce([
            boundary_mask[i:i+height, j:j+width]
            for i in range(2*BOUNDARY_DILATION_SIZE+1)
            for j in range(2*BOUNDARY_DILATION_SIZE+1)
        ])
    
    # 境界部分で色の類似度が高い部分を透過
    data[:, :, 3] = np.where(
        boundary_mask & boundary_color_mask & is_foreground,
        0,
        data[:, :, 3]
    )
    
    return Image.fromarray(data)

def process_image(input_data: bytes, mode: str) -> bytes:
    """
    画像を処理して背景を削除する
    
    Args:
        input_data: 入力画像のバイトデータ
        mode: 背景削除モード（"auto" または "rembg"）
        
    Returns:
        bytes: 処理済み画像のバイトデータ
    """
    if mode == "auto":
        # 自動背景色検出モード
        image = Image.open(io.BytesIO(input_data))
        background_color = detect_background_color(image)
        print(f"検出された背景色: RGB{background_color}")
        processed_image = remove_background_color(image, background_color)
        output = io.BytesIO()
        processed_image.save(output, format="PNG")
        return output.getvalue()
    else:
        # rembgモード
        return remove(
            input_data,
            alpha_matting=ALPHA_MATTING,
            alpha_matting_foreground_threshold=ALPHA_MATTING_FOREGROUND_THRESHOLD,
            alpha_matting_background_threshold=ALPHA_MATTING_BACKGROUND_THRESHOLD,
            alpha_matting_erode_size=ALPHA_MATTING_ERODE_SIZE,
            post_process_mask=POST_PROCESS_MASK
        )

def main():
    """
    メイン処理
    
    処理の流れ:
    1. コマンドライン引数の解析
    2. 入力ディレクトリの検証
    3. 出力ディレクトリの準備
    4. 画像の処理
       - 背景の削除
       - 前景のスケーリングと中央配置
       - 出力サイズへの調整
    5. 結果の出力
    """
    prefix, input_dir, output_dir, mode, output_size = parse_arguments()
    
    # 設定値の出力
    print("\n=== 設定 ====")
    print(f"入力ディレクトリ: {input_dir}")
    print(f"出力ディレクトリ: {output_dir}")
    print(f"背景削除モード: {mode}")
    print(f"プレフィックス: {prefix if prefix else '(なし)'}")
    if output_size:
        print(f"出力サイズ: {output_size[0]}x{output_size[1]}")
    else:
        print("出力サイズ: 元画像のサイズを使用")
    print("=============\n")
    
    validate_input(input_dir)

    # 出力ディレクトリの処理
    has_gitkeep = False
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
                # プレフィックスが空の場合は元のファイル名をそのまま使用
                if prefix:
                    output_name = f"{prefix}_{counter}_{base_name}.png"
                else:
                    output_name = f"{base_name}.png"
                output_path = os.path.join(output_dir, output_name)

                with open(input_path, 'rb') as i:
                    input_data = i.read()
                    output_data = process_image(input_data, mode)

                    image = Image.open(io.BytesIO(output_data)).convert("RGBA")
                    centered_scaled = scale_foreground(image, output_size=output_size)
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
        print(f"使用モード: {mode}")
        if output_size:
            print(f"出力サイズ: {output_size[0]}x{output_size[1]}")
        else:
            print("出力サイズ: 元画像のサイズを使用")

if __name__ == "__main__":
    main()

