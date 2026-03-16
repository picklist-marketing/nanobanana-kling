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
    character_emotion = form_data.get('character_emotion', 'panicked and terrified')
    visual_style = form_data.get('visual_style', 'grotesque comedy, Pixar meets body horror')
    camera_angle = form_data.get('camera_angle', 'extreme close-up POV from inside')

    # 環境と色、質感を自動推測
    environment = get_environment_from_subject(character_subject)
    character_color = get_character_color(character_subject)
    character_texture = get_character_texture(character_subject)

    # Nano Banana プロンプト（シンプル版）
    nano_banana_prompt = f"""A tiny {character_color} cartoon character representing {character_subject},
with HUGE bulging eyes and exaggerated {character_emotion} expression,
wide open mouth showing teeth,
{character_texture},
small stubby arms and legs waving expressively,
cute yet grotesque appearance,
trapped inside {environment},
surrounded by realistic biological details,
POV from {camera_angle} perspective,
3D rendered in {visual_style} style,
IMPORTANT: Character must have CLEAR FACIAL FEATURES - large expressive eyes, defined mouth, anime-style character design,
NOT photorealistic biological blob, but a CHARACTER with personality,
Character's body texture and appearance should match the actual look of {character_subject},
hyperrealistic environment contrasting with stylized cartoon character,
dramatic lighting with biological wetness and organic textures,
highly detailed, octane render, 8k,
Pixar animation quality character in medical illustration environment,
vertical portrait orientation, 9:16 aspect ratio,
NO TEXT, NO WORDS, NO LETTERS in the image"""

    # Kling プロンプト（構造化フォーマット）
    kling_sections = []

    # Subject
    kling_sections.append(f"""Subject:
A grotesque but cartoonish {character_subject} creature with huge bulging eyes and tiny arms standing inside {environment}. The character has {character_texture}, designed to look like an actual {character_subject} but with anime-style facial features.""")

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
The {character_subject} character suddenly reacts with {character_emotion} emotion and shouts toward the camera:

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
The {character_subject} character shows {character_emotion} emotion through exaggerated body language.

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

    kling_prompt = "\n\n".join(kling_sections)

    return nano_banana_prompt.strip(), kling_prompt.strip()


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
    print("🎨 Nano Banana × Kling プロンプト生成UI v4.1")
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
