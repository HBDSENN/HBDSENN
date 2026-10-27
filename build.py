import os
import json

# 큰 PNG 원본은 상세 페이지에서만 쓰고, 목록·배경에는 가벼운 미리보기(webp)를 씁니다.
# Pillow가 없으면 미리보기 없이 원본으로 동작합니다. (설치: pip install pillow)
try:
    from PIL import Image
except ImportError:
    Image = None

THUMB_DIR = '_thumbs'
THUMB_WIDTH = 1920


def make_thumb(img_path):
    if Image is None:
        return ""
    name = img_path.replace('/', '__').rsplit('.', 1)[0] + '.webp'
    out = f"{THUMB_DIR}/{name}"
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(img_path):
        return out
    os.makedirs(THUMB_DIR, exist_ok=True)
    with Image.open(img_path) as im:
        im = im.convert('RGB')
        if im.width > THUMB_WIDTH:
            im = im.resize((THUMB_WIDTH, round(im.height * THUMB_WIDTH / im.width)), Image.LANCZOS)
        im.save(out, 'WEBP', quality=82)
    return out


def get_folder_data(base_dir):
    data = {}
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        return data

    for folder_name in sorted(os.listdir(base_dir)):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path):
            clean_title = folder_name.split('_', 1)[-1] if '_' in folder_name else folder_name
            images = []
            youtube_link = ""

            # cover.txt 에 파일 이름을 적으면 그 이미지가 대표(목록·배경) 이미지가 됩니다. 없으면 첫 이미지.
            cover_name = ""
            cover_file = os.path.join(folder_path, "cover.txt")
            if os.path.exists(cover_file):
                with open(cover_file, 'r', encoding='utf-8') as f:
                    cover_name = f.read().strip()

            youtube_file = os.path.join(folder_path, "youtube.txt")
            if os.path.exists(youtube_file):
                with open(youtube_file, 'r', encoding='utf-8') as f:
                    youtube_link = f.read().strip()

            for file_name in sorted(os.listdir(folder_path)):
                # 이미지 파일만 골라냅니다
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    img_path = f"{base_dir}/{folder_name}/{file_name}"
                    images.append(img_path)

            if images:
                cover_index = next((i for i, p in enumerate(images) if p.endswith('/' + cover_name)), 0) if cover_name else 0
                data[folder_name] = {
                    "title": clean_title,
                    "images": images,
                    "thumbs": [make_thumb(p) for p in images],
                    "cover": cover_index,
                    "youtube": youtube_link
                }
    return data

print("삐뽀! 폴더들을 스캔하는 중입니다...")

motorsports_data = get_folder_data('Motorsports')
portfolio_data = get_folder_data('Portfolio')

js_content = f"const motorSportsData = {json.dumps(motorsports_data, ensure_ascii=False, indent=4)};\n"
js_content += f"const portfolioData = {json.dumps(portfolio_data, ensure_ascii=False, indent=4)};\n"

with open('data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("삐뽀! 2개의 카테고리가 data.js에 완벽하게 빌드되었습니다!")
if Image is None:
    print("(참고) Pillow가 없어 미리보기 이미지는 만들지 않았습니다. pip install pillow 후 다시 실행하면 사이트가 더 빨라집니다.")
