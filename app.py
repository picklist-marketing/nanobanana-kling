#!/usr/bin/env python3
"""
Nano Banana × Kling プロンプト生成/管理 Web UI
Kling公式フォーマット対応版（構造化 + セリフ対応）
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime
from pathlib import Path
from deep_translator import GoogleTranslator
import google.generativeai as genai
from dotenv import load_dotenv
import time
import base64
import requests

# プロジェクトディレクトリを明示的に指定
PROJECT_DIR = Path(__file__).parent
app = Flask(__name__,
            static_folder=str(PROJECT_DIR / 'static'),
            template_folder=str(PROJECT_DIR / 'templates'))

# 環境変数をロード
load_dotenv(PROJECT_DIR / '.env')

# Google AI APIの初期化
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(f"✅ Google AI API initialized")
else:
    print("⚠️  Warning: GOOGLE_API_KEY not found in .env file")

# Vercel環境かどうかを判定
IS_VERCEL = os.environ.get('VERCEL') == '1'

# 出力ディレクトリ（Vercelでは/tmpを使用）
if IS_VERCEL:
    OUTPUTS_DIR = Path("/tmp/outputs")
else:
    OUTPUTS_DIR = PROJECT_DIR / "outputs"
HISTORY_FILE = OUTPUTS_DIR / "prompt-history.json"


def translate_to_english(text):
    """日本語テキストを英語に翻訳（セリフや演出指示用）"""
    if not text or not text.strip():
        return text

    # 英語のみの場合はそのまま返す（簡易判定）
    if all(ord(char) < 128 or char in ' \n\t.,!?\'"' for char in text):
        return text

    try:
        # Google Translateで翻訳
        translator = GoogleTranslator(source='ja', target='en')
        translated = translator.translate(text)

        # 翻訳が成功したか確認（空でない、元のテキストと異なる）
        if translated and translated.strip() and translated != text:
            print(f"Translation success: '{text}' -> '{translated}'")
            return translated
        else:
            print(f"Translation returned same text: '{text}'")
            # フォールバック: 簡易翻訳辞書を使用
            return simple_translate(text)
    except Exception as e:
        # 翻訳失敗時は簡易翻訳にフォールバック
        print(f"Translation error: {e}. Falling back to simple translation.")
        return simple_translate(text)


def simple_translate(text):
    """簡易翻訳辞書（フォールバック用）"""
    # よく使われるフレーズの辞書
    phrases = {
        'みんな、もうお前の口臭に気づいてるぞ': 'Everyone already knows about your bad breath',
        '助けて': 'Help me',
        'やめて': 'Stop it',
        '痛い': 'It hurts',
        '気持ちいい': 'It feels good',
        'ありがとう': 'Thank you',
        'さようなら': 'Goodbye',
        'こんにちは': 'Hello',
    }

    # 完全一致を探す
    if text in phrases:
        return phrases[text]

    # 部分一致を探す
    for jp, en in phrases.items():
        if jp in text:
            return text.replace(jp, en)

    # 該当なしの場合は元のテキストを返す
    print(f"No translation available for: '{text}'")
    return text


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
    """セリフからリップシンク指示を生成（日本語対応）"""
    if not dialogue or not dialogue.strip():
        return ""

    # 日本語が含まれているかチェック
    has_japanese = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in dialogue)

    if has_japanese:
        # 日本語の場合：より自然なリップシンク指示
        dialogue_clean = dialogue.strip()

        # 感情表現を判定
        is_exclamation = dialogue_clean.endswith('！') or dialogue_clean.endswith('!') or '！！' in dialogue_clean
        is_question = dialogue_clean.endswith('？') or dialogue_clean.endswith('?')

        lip_sync_parts = []

        if is_exclamation:
            # 叫び・強調の場合
            lip_sync_parts.append(f'日本語セリフ: "{dialogue_clean}"')
            lip_sync_parts.append('口を大きく開けて感情的に叫ぶ')
            lip_sync_parts.append('表情は強い感情（怒り・恐怖・驚き）を表現')
            lip_sync_parts.append('口の動きは大きく、ダイナミックに')
            lip_sync_parts.append('最後の音で口を最大限に開く')
        elif is_question:
            # 質問の場合
            lip_sync_parts.append(f'日本語セリフ: "{dialogue_clean}"')
            lip_sync_parts.append('口の動きは自然で、語尾で少し上がる')
            lip_sync_parts.append('表情は疑問や困惑を示す')
        else:
            # 通常の会話
            lip_sync_parts.append(f'日本語セリフ: "{dialogue_clean}"')
            lip_sync_parts.append('自然な日本語の口の動き')
            lip_sync_parts.append('母音（あ・い・う・え・お）の口の形を明確に')
            lip_sync_parts.append('表情と口の動きが完全に同期')

        return '\n'.join(lip_sync_parts)
    else:
        # 英語の場合：従来の処理
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

    # 各フィールドを英語に翻訳
    character_subject_en = translate_subject_to_english(character_subject)
    dialogue_en = dialogue if dialogue else ''  # 日本語のまま使用（翻訳しない）
    additional_direction_en = translate_to_english(additional_direction) if additional_direction else ''

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
    if additional_direction_en:
        nano_banana_prompt += f"\n\nADDITIONAL DIRECTION:\n{additional_direction_en}"

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
    if dialogue_en:
        # セリフありの場合
        lip_sync = generate_lip_sync(dialogue_en)

        # 日本語かどうかをチェック
        has_japanese = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in dialogue_en)

        if has_japanese:
            # 日本語セリフの場合
            kling_sections.append(f"""Action:
The {character_subject_en} character suddenly reacts with {character_emotion} emotion and speaks in Japanese toward the camera.

DIALOGUE (Japanese audio with perfect lip sync):
{lip_sync}

Character performance:
- Mouth movements perfectly synchronized with Japanese phonetics
- Clear articulation of vowel sounds (あ・い・う・え・お shapes)
- Expression matches the emotional tone of the dialogue
- Tiny arms gesture dramatically to emphasize the words
- Body language reinforces the meaning and emotion

Animation details:
- Eyes vibrate and bulge dramatically to show emotion
- Body wobbles in rubber-hose cartoon style while speaking
- Surrounding biological elements (saliva/moisture) react to the shouting
- Character leans forward with intensity
- Facial expressions change naturally throughout the dialogue
- Perfect timing between audio and lip movements""")
        else:
            # 英語セリフの場合
            kling_sections.append(f"""Action:
The {character_subject_en} character suddenly reacts with {character_emotion} emotion and shouts toward the camera:

"{dialogue_en}"

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
    if additional_direction_en:
        kling_sections.append(f"""Additional Direction:
{additional_direction_en}""")

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


@app.route('/gallery')
def gallery():
    """ギャラリーページ"""
    return render_template('gallery.html')


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


def generate_image_with_imagen(prompt):
    """Imagen 4.0で画像を生成（REST API使用）"""
    try:
        # 出力ディレクトリを確保
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        print(f"\n🎨 Imagen 4.0 画像生成開始...")
        print(f"プロンプト: {prompt[:100]}...")

        # Google AI REST APIエンドポイント（Imagen 4.0 Fast）
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-fast-generate-001:predict?key={GOOGLE_API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "instances": [{
                "prompt": prompt
            }],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "9:16",
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_all"
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        result = response.json()
        print(f"API Response: {result}")

        # 画像データを取得（base64エンコードされている）
        if 'predictions' in result and len(result['predictions']) > 0:
            prediction = result['predictions'][0]

            # レスポンス形式を確認
            if 'bytesBase64Encoded' in prediction:
                image_b64 = prediction['bytesBase64Encoded']
            elif 'image' in prediction and 'bytesBase64Encoded' in prediction['image']:
                image_b64 = prediction['image']['bytesBase64Encoded']
            else:
                raise Exception(f"Unknown response format: {prediction}")

            image_data = base64.b64decode(image_b64)

            # 画像を保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"generated_image_{timestamp}.png"
            image_path = OUTPUTS_DIR / image_filename

            with open(image_path, 'wb') as f:
                f.write(image_data)

            print(f"✅ 画像生成完了: {image_filename}")

            return {
                'success': True,
                'image_path': str(image_path),
                'image_filename': image_filename,
                'image_url': f'/outputs/{image_filename}'
            }
        else:
            raise Exception(f"No predictions in response: {result}")

    except Exception as e:
        print(f"❌ Imagen 4.0エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def generate_video_with_veo(prompt, image_path=None, dialogue=None):
    """Veo 3.1で動画を生成（REST API使用）"""
    try:
        # 出力ディレクトリを確保
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        print(f"\n🎬 Veo 3.1 動画生成開始...")
        print(f"プロンプト: {prompt[:100]}...")
        if dialogue:
            print(f"セリフ: {dialogue}")

        # セリフがある場合は音声指示を追加
        if dialogue:
            full_prompt = f"{prompt}\n\nThe character speaks in Japanese: \"{dialogue}\"\nGenerate matching lip sync and voice audio."
        else:
            full_prompt = prompt

        # Google AI REST APIエンドポイント（Veo 3.1 Fast）
        url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning?key={GOOGLE_API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "instances": [{
                "prompt": full_prompt
            }],
            "parameters": {
                "aspectRatio": "9:16"
            }
        }

        # 画像がある場合は画像データを追加
        if image_path and Path(image_path).exists():
            print(f"📸 画像から動画生成: {image_path}")
            with open(image_path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode('utf-8')
            # 画像データを正しい構造で送信（bytesBase64EncodedとmimeTypeが必要）
            payload["instances"][0]["image"] = {
                "bytesBase64Encoded": image_b64,
                "mimeType": "image/png"
            }

        print(f"🚀 動画生成リクエスト送信中...")
        response = requests.post(url, headers=headers, json=payload, timeout=300)

        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        result = response.json()
        print(f"API Response: {result}")

        # predictLongRunningはoperation IDを返す
        if 'name' in result:
            # Long-running operationの場合
            operation_name = result['name']
            print(f"⏳ 動画生成中... Operation: {operation_name}")

            # Operationのステータスをポーリング
            max_attempts = 60  # 最大5分（5秒 × 60回）
            for attempt in range(max_attempts):
                print(f"⏳ ポーリング中... ({attempt + 1}/{max_attempts})")
                time.sleep(5)  # 5秒待機

                # Operation状態を確認
                op_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={GOOGLE_API_KEY}"
                op_response = requests.get(op_url)

                if op_response.status_code != 200:
                    print(f"⚠️  Operation status check failed: {op_response.text}")
                    continue

                op_result = op_response.json()
                print(f"Operation status: {op_result.get('done', False)}")

                # 完了チェック
                if op_result.get('done', False):
                    print(f"✅ 動画生成完了！")

                    # エラーチェック
                    if 'error' in op_result:
                        raise Exception(f"Operation failed: {op_result['error']}")

                    # 結果を取得
                    if 'response' in op_result:
                        result = op_result['response']
                        break
                    else:
                        raise Exception(f"No response in completed operation: {op_result}")

            else:
                # タイムアウト
                raise Exception(f"Video generation timed out after {max_attempts * 5} seconds")

        # 動画データを取得
        video_data = None

        # レスポンス形式1: generateVideoResponse（URI形式）
        if 'generateVideoResponse' in result:
            generated_samples = result['generateVideoResponse'].get('generatedSamples', [])
            if generated_samples and 'video' in generated_samples[0]:
                video_uri = generated_samples[0]['video'].get('uri')
                if video_uri:
                    print(f"📥 動画をダウンロード中: {video_uri}")
                    # URIから動画をダウンロード（API keyを追加）
                    download_url = f"{video_uri}&key={GOOGLE_API_KEY}" if '?' in video_uri else f"{video_uri}?key={GOOGLE_API_KEY}"
                    video_response = requests.get(download_url, timeout=120)
                    if video_response.status_code == 200:
                        video_data = video_response.content
                        print(f"✅ 動画ダウンロード完了: {len(video_data)} bytes")
                    else:
                        raise Exception(f"Failed to download video: {video_response.status_code} {video_response.text}")

        # レスポンス形式2: predictions（base64形式）
        elif 'predictions' in result and len(result['predictions']) > 0:
            prediction = result['predictions'][0]
            if 'bytesBase64Encoded' in prediction:
                video_b64 = prediction['bytesBase64Encoded']
            elif 'video' in prediction and 'bytesBase64Encoded' in prediction['video']:
                video_b64 = prediction['video']['bytesBase64Encoded']
            else:
                raise Exception(f"Unknown prediction format: {prediction}")
            video_data = base64.b64decode(video_b64)

        if video_data:
            # 動画を保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"generated_video_{timestamp}.mp4"
            video_path = OUTPUTS_DIR / video_filename

            with open(video_path, 'wb') as f:
                f.write(video_data)

            print(f"✅ 動画保存完了: {video_filename}")

            return {
                'success': True,
                'video_path': str(video_path),
                'video_filename': video_filename,
                'video_url': f'/outputs/{video_filename}'
            }
        else:
            raise Exception(f"No video data in response: {result}")

    except Exception as e:
        print(f"❌ Veo 3.1エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    """画像生成APIエンドポイント"""
    try:
        data = request.json
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'success': False, 'error': 'プロンプトが必要です'}), 400

        if not GOOGLE_API_KEY:
            return jsonify({'success': False, 'error': 'Google API Keyが設定されていません'}), 500

        result = generate_image_with_imagen(prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    """動画生成APIエンドポイント"""
    try:
        data = request.json
        prompt = data.get('prompt')
        image_filename = data.get('image_filename')
        dialogue = data.get('dialogue', '')

        if not prompt:
            return jsonify({'success': False, 'error': 'プロンプトが必要です'}), 400

        if not GOOGLE_API_KEY:
            return jsonify({'success': False, 'error': 'Google API Keyが設定されていません'}), 500

        # 画像パスを取得
        image_path = None
        if image_filename:
            image_path = str(OUTPUTS_DIR / image_filename)

        result = generate_video_with_veo(prompt, image_path, dialogue)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-full', methods=['POST'])
def api_generate_full():
    """画像→動画の一括生成APIエンドポイント"""
    try:
        data = request.json
        image_prompt = data.get('image_prompt')
        video_prompt = data.get('video_prompt')
        dialogue = data.get('dialogue', '')

        if not image_prompt or not video_prompt:
            return jsonify({'success': False, 'error': 'プロンプトが必要です'}), 400

        if not GOOGLE_API_KEY:
            return jsonify({'success': False, 'error': 'Google API Keyが設定されていません'}), 500

        # 1. 画像生成
        image_result = generate_image_with_imagen(image_prompt)
        if not image_result['success']:
            return jsonify(image_result), 500

        # 2. 動画生成
        video_result = generate_video_with_veo(
            video_prompt,
            image_result['image_path'],
            dialogue
        )

        if not video_result['success']:
            return jsonify(video_result), 500

        # 両方成功
        return jsonify({
            'success': True,
            'image': image_result,
            'video': video_result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/outputs/<filename>')
def serve_output(filename):
    """生成したファイルを配信"""
    file_path = OUTPUTS_DIR / filename
    if file_path.exists():
        return send_file(file_path)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("🎬 アニメCR作るくん v5.0")
    print("="*70)
    print(f"\n✅ サーバー起動: http://localhost:5051")
    print(f"✅ LAN接続: http://0.0.0.0:5051")
    print("\n📁 プロジェクト: ~/Projects/nanobanana-kling")
    print(f"📊 履歴ファイル: {HISTORY_FILE}")
    print(f"🎬 出力ディレクトリ: {OUTPUTS_DIR}")
    print("\n🚀 Google AI統合:")
    print("  ✅ Imagen 3（画像生成）")
    print("  ✅ Veo 3.1（動画生成）- 日本語音声対応")
    print("  ✅ 自動生成機能（画像→動画）")
    print("\n💡 機能:")
    print("  ✨ プロンプト自動生成")
    print("  ✨ セリフ入力対応（日本語OK）")
    print("  ✨ 自動リップシンク生成")
    print("  ✨ 縦長動画対応（9:16）")
    print("\n" + "="*70 + "\n")

    app.run(host='0.0.0.0', port=5051, debug=True)
