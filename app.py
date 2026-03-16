#!/usr/bin/env python3
"""
Nano Banana × Kling プロンプト生成/管理 Web UI
Kling公式フォーマット対応版（構造化 + セリフ対応）
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from pathlib import Path

# プロジェクトディレクトリを明示的に指定
PROJECT_DIR = Path(__file__).parent
app = Flask(__name__,
            static_folder=str(PROJECT_DIR / 'static'),
            template_folder=str(PROJECT_DIR / 'templates'))

# Vercel環境かどうかを判定
IS_VERCEL = os.environ.get('VERCEL') == '1'

# 出力ディレクトリ
OUTPUTS_DIR = PROJECT_DIR / "outputs"
HISTORY_FILE = OUTPUTS_DIR / "prompt-history.json"


def translate_subject_to_english(subject):
    """日本語のキャラクター対象を英語に翻訳"""
    # 複合語の完全一致（優先）
    full_translations = {
        '顔の角栓': 'facial keratin plug',
        '鼻の角栓': 'nose keratin plug',
        '毛穴の角栓': 'pore keratin plug',
        '頬の角栓': 'cheek keratin plug',
        '小鼻の角栓': 'nostril keratin plug',
        '頭皮の皮脂': 'scalp sebum',
        '顔の皮脂': 'facial sebum',
        '口の中': 'inside mouth',
        '口の中の細菌': 'oral bacteria',
    }

    # 完全一致を最優先で探す
    if subject in full_translations:
        return full_translations[subject]

    # 基本的な単語翻訳
    translations = {
        '歯垢': 'dental plaque',
        '歯': 'tooth',
        '舌': 'tongue',
        '口': 'mouth',
        '口腔': 'oral cavity',
        '毛根': 'hair follicle',
        '頭皮': 'scalp',
        '髪': 'hair',
        '角栓': 'keratin plug',
        '毛穴': 'skin pore',
        '皮脂': 'sebum',
        '油': 'oil',
        '汗': 'sweat',
        '肌': 'skin',
        '顔': 'face',
        '鼻': 'nose',
        '頬': 'cheek',
        '小鼻': 'nostril',
        '細菌': 'bacteria',
        '腸': 'intestine',
        '胃': 'stomach',
        '血管': 'blood vessel',
    }

    # 完全一致を探す
    if subject in translations:
        return translations[subject]

    # 「AのB」パターンを処理
    if 'の' in subject:
        parts = subject.split('の')
        translated_parts = []
        for part in parts:
            if part in translations:
                translated_parts.append(translations[part])
            elif part:  # 空でない場合はそのまま残す
                translated_parts.append(part)

        # 英語の順序に変換（「顔の角栓」→「face keratin plug」）
        if len(translated_parts) >= 2:
            return ' '.join(translated_parts)

    # 部分一致を探す（長い方から優先）
    result = subject
    for jp, en in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        if jp in result:
            result = result.replace(jp, en)

    return result


def get_environment_from_subject(subject):
    """キャラクター対象から環境を推測"""
    if any(word in subject for word in ['歯垢', '歯', '舌', '口']):
        return "inside mouth cavity with teeth and tongue"
    elif any(word in subject for word in ['毛根', '頭皮', '髪']):
        return "scalp with hair follicles and pores"
    elif any(word in subject for word in ['角栓', '毛穴', '皮脂', '肌']):
        return "inside skin pore with surrounding tissue"
    elif any(word in subject for word in ['腸', '胃', '血管']):
        return "inside body cavity with organic tissues"
    else:
        return "biological or household environment"


def get_character_color(subject):
    """キャラクター対象から色を推測"""
    if '歯垢' in subject:
        return "yellowish-green crusty"
    elif '舌' in subject:
        return "pink fleshy"
    elif '毛根' in subject:
        return "pinkish white"
    elif '皮脂' in subject or '油' in subject:
        return "yellowish oily"
    elif '角栓' in subject:
        return "dirty white waxy"
    return "pink fleshy"


def get_character_texture(subject):
    """キャラクター対象から質感・形状を推測"""
    if '歯垢' in subject:
        return "crusty rough plaque-like surface with yellowish-green patches, hard calcified edges"
    elif '舌' in subject:
        return "soft fleshy bumpy texture with visible papillae bumps on surface"
    elif '毛根' in subject:
        return "root-like elongated shape with bulbous bottom, smooth white follicle surface"
    elif '皮脂' in subject or '油' in subject:
        return "shiny oily slick surface, semi-transparent yellowish glow, liquid-like consistency"
    elif '角栓' in subject:
        return "waxy hardened sebum texture, compacted white-yellowish plug, solid compressed keratin"
    return "biological organic texture matching the actual appearance of the subject"


def generate_lip_sync(dialogue):
    """セリフからリップシンク指示を生成"""
    words = dialogue.upper().split()
    lip_sync = []

    for i, word in enumerate(words):
        if i == 0:
            lip_sync.append(f'"{word}" – mouth opens very wide, jaw drops dramatically')
        elif i == len(words) - 1:
            if word.endswith('!!') or word.endswith('!'):
                lip_sync.append(f'"{word}" – character screams loudly with mouth stretched extremely wide')
            else:
                lip_sync.append(f'"{word}" – mouth closes slightly, emphasizing final word')
        else:
            lip_sync.append(f'"{word}" – tongue/mouth moves naturally while speaking')

    return "\n".join(lip_sync)


def generate_prompts(form_data):
    """
    Kling公式フォーマットでプロンプトを生成
    """
    # フォームデータ取得
    product_category = form_data.get('product_category', '')
    character_subject = form_data.get('character_subject', '')
    dialogue = form_data.get('dialogue', '').strip()
    additional_direction = form_data.get('additional_direction', '').strip()
    character_emotion = form_data.get('character_emotion', 'panicked and terrified')
    visual_style = form_data.get('visual_style', 'grotesque comedy, Pixar meets body horror')
    camera_angle = form_data.get('camera_angle', 'extreme close-up POV from inside')

    # キャラクター対象を英語に翻訳
    character_subject_en = translate_subject_to_english(character_subject)

    # 環境と色、質感を自動推測（英語版を使用）
    environment = get_environment_from_subject(character_subject_en)
    character_color = get_character_color(character_subject_en)
    character_texture = get_character_texture(character_subject_en)

    # Nano Banana プロンプト（シンプル版）
    nano_banana_prompt = f"""An anthropomorphized {character_subject_en} cartoon character - literally a {character_subject_en} transformed into a cute character with a face.

CHARACTER DETAILS:
- The character IS a {character_subject_en} with cartoon features added
- Body shape and structure based on actual {character_subject_en} anatomy
- {character_texture}
- {character_color} coloring matching real {character_subject_en}
- Tiny {character_subject_en} body with adorable cartoon modifications

FACIAL FEATURES (CRITICAL):
- HUGE bulging expressive eyes (anime-style, NOT realistic)
- Wide open mouth showing teeth
- Clear defined facial features with personality
- Exaggerated {character_emotion} expression
- NOT a photorealistic blob - this is a CHARACTER with emotions

BODY:
- Small stubby arms and legs added to the {character_subject_en} body
- Arms waving expressively
- Cute yet grotesque appearance
- Maintains recognizable {character_subject_en} characteristics

ENVIRONMENT:
- Trapped inside {environment}
- Surrounded by hyperrealistic biological details
- POV from {camera_angle} perspective
- Environment contrasts with stylized cartoon character

STYLE:
- 3D rendered in {visual_style} style
- Pixar animation quality character design
- Medical illustration environment
- Dramatic lighting with biological wetness and organic textures
- Highly detailed, octane render, 8k
- Vertical portrait orientation, 9:16 aspect ratio

NO TEXT, NO WORDS, NO LETTERS in the image"""

    # 追加の演出指示があれば追加
    if additional_direction:
        nano_banana_prompt += f"\n\nADDITIONAL DIRECTION:\n{additional_direction}"

    nano_banana_prompt = nano_banana_prompt.strip()

    # Kling プロンプト（構造化フォーマット）
    kling_sections = []

    # Subject
    kling_sections.append(f"""Subject:
An anthropomorphized {character_subject_en} character - literally a {character_subject_en} transformed into a cartoon creature with a face and personality. The character IS a {character_subject_en} with huge bulging eyes, tiny arms and legs added. Body structure and appearance match an actual {character_subject_en}: {character_texture}, {character_color} coloring. This is NOT a generic blob but specifically recognizable as a {character_subject_en}. Standing inside {environment}.""")

    # Context
    context_desc = ""
    if 'mouth' in environment:
        context_desc = "The inside of the mouth is extremely slimy and sticky. Thick saliva stretches between dirty teeth and gums. Plaque and grime cover the teeth. The environment looks wet, disgusting, and uncomfortable."
    elif 'scalp' in environment or 'hair' in environment:
        context_desc = "The scalp surface is covered with pores and hair follicles. Sebum and oils create a shiny, sticky surface. The environment looks biological and microscopic."
    elif 'pore' in environment or 'skin' in environment:
        context_desc = "Inside the skin pore, sebum and dead skin cells create a clogged, sticky environment. The walls are organic tissue. Everything looks wet and biological."
    else:
        context_desc = f"The environment is biological and organic. Wet textures and organic materials surround the character. The atmosphere is uncomfortable and visceral."

    kling_sections.append(f"""Context:
{context_desc}""")

    # Action（セリフあり/なし）
    if dialogue:
        # セリフありの場合
        lip_sync = generate_lip_sync(dialogue)
        kling_sections.append(f"""Action:
The {character_subject_en} character suddenly reacts with {character_emotion} emotion and shouts toward the camera:

"{dialogue}"

Lip sync animation:
{lip_sync}

The character gestures dramatically with tiny arms while speaking.

Comedic animation:
- Eyes vibrate and bulge dramatically
- Body wobbles in rubber-hose cartoon style
- Surrounding biological elements (saliva/moisture) stretch and shake as character shouts
- Character leans forward aggressively while yelling""")
    else:
        # セリフなしの場合
        kling_sections.append(f"""Action:
The {character_subject_en} character shows {character_emotion} emotion through exaggerated body language.

Animation:
- HUGE EYES widening dramatically
- Mouth opening wider in exaggerated expression
- Facial features animating intensely
- Small arms and legs flailing expressively
- Body wobbles in rubber-hose cartoon style

Comedic animation:
- Eyes vibrate and bulge
- Body moves with cartoon physics
- Surrounding biological elements react to movement
- Character shows intense emotional reaction""")

    # Style
    style_desc = "Pixar-style 3D animation"
    if "grotesque" in visual_style:
        style_desc += ", exaggerated cartoon acting, expressive facial animation, comedic gross humor"
    elif "cute" in visual_style:
        style_desc += ", cute character design, friendly animation, warm colors"

    kling_sections.append(f"""Style:
{style_desc}.""")

    # Camera Movement
    camera_desc = ""
    if "extreme close-up" in camera_angle:
        camera_desc = "Extreme close-up shot, slow push-in zoom emphasizing character's reaction, slight camera shake during intense moments."
    elif "surface level" in camera_angle:
        camera_desc = "Low angle camera looking up at character, slow dolly movement, dynamic framing."
    else:
        camera_desc = "Dynamic camera movement following character's action, slight shake for emphasis."

    kling_sections.append(f"""Camera Movement:
{camera_desc}""")

    # Composition
    kling_sections.append(f"""Composition:
Vertical 9:16 format (portrait orientation).
Ultra close-up framing of the character inside {environment}, surrounded by biological details.""")

    # Ambiance & Effects
    effects_desc = []
    if 'mouth' in environment:
        effects_desc = [
            "Sticky saliva strands stretching between teeth",
            "Wet mouth textures",
            "Moisture dripping and flowing"
        ]
    elif 'scalp' in environment:
        effects_desc = [
            "Oily sebum on surfaces",
            "Hair follicles visible in background",
            "Microscopic skin texture details"
        ]
    elif 'pore' in environment:
        effects_desc = [
            "Sebum and oils in pore",
            "Organic skin tissue walls",
            "Moist biological textures"
        ]
    else:
        effects_desc = [
            "Wet organic textures",
            "Biological moisture effects",
            "Visceral environmental details"
        ]

    kling_sections.append(f"""Ambiance & Effects:
{chr(10).join('- ' + effect for effect in effects_desc)}""")

    # 追加の演出指示があれば追加
    if additional_direction:
        kling_sections.append(f"""Additional Direction:
{additional_direction}""")

    kling_prompt = "\n\n".join(kling_sections)

    return nano_banana_prompt, kling_prompt.strip()


def load_history():
    """プロンプト履歴を読み込み"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(entry):
    """プロンプト履歴に保存"""
    history = load_history()
    entry['timestamp'] = datetime.now().isoformat()
    entry['id'] = len(history) + 1
    history.insert(0, entry)
    history = history[:100]

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return entry


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """プロンプトを生成"""
    form_data = request.json
    nano_prompt, kling_prompt = generate_prompts(form_data)

    return jsonify({
        'nano_banana': nano_prompt,
        'kling': kling_prompt
    })


@app.route('/api/history')
def get_history():
    """履歴を取得"""
    if IS_VERCEL:
        # Vercel環境では空配列を返す（クライアント側でlocalStorage使用）
        return jsonify([])
    return jsonify(load_history())


@app.route('/api/save', methods=['POST'])
def save_prompt():
    """プロンプトを保存"""
    if IS_VERCEL:
        # Vercel環境では保存しない（クライアント側でlocalStorage使用）
        return jsonify({'success': True, 'message': 'Saved to localStorage'})
    data = request.json
    entry = save_history(data)
    return jsonify(entry)


@app.route('/api/delete/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """プロンプトを削除"""
    if IS_VERCEL:
        # Vercel環境では何もしない（クライアント側でlocalStorage使用）
        return jsonify({'success': True})

    history = load_history()
    history = [h for h in history if h.get('id') != prompt_id]

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return jsonify({'success': True})


if __name__ == '__main__':
    OUTPUTS_DIR.mkdir(exist_ok=True)

    print("\n" + "="*70)
    print("🎨 Nano Banana × Kling プロンプト生成UI v4.2")
    print("="*70)
    print(f"\n✅ サーバー起動: http://localhost:5051")
    print(f"✅ LAN接続: http://0.0.0.0:5051")
    print("\n📁 プロジェクト: ~/Projects/nanobanana-kling")
    print(f"📊 履歴ファイル: {HISTORY_FILE}")
    print("\n💡 新機能:")
    print("  ✨ Kling公式フォーマット対応（構造化プロンプト）")
    print("  ✨ セリフ入力対応（任意）")
    print("  ✨ 自動リップシンク生成")
    print("  ✨ Subject/Context/Action/Style/Camera/Composition/Effects")
    print("\n" + "="*70 + "\n")

    app.run(host='0.0.0.0', port=5051, debug=True)
