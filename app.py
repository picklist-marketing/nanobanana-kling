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


def generate_kinnikukun_prompts(form_data):
    """筋肉くんキャラクター用のプロンプトを生成"""
    character = form_data.get('kinnikukun_character', 'muscle-duo')
    scene = form_data.get('kinnikukun_scene', 'gym')
    expression = form_data.get('kinnikukun_expression', 'rage')
    dialogue = form_data.get('dialogue', '').strip()
    additional_direction = form_data.get('additional_direction', '').strip()

    character_details = {
        'muscle-duo': {
            'name': 'Muscle Duo',
            'desc': 'Two 3D characters resembling realistic human anatomy muscle models with visible red muscles and no skin. The larger character has a big protruding belly, the smaller one is slim and athletic.',
        },
        'muscle-big': {
            'name': 'Big Muscle Guy',
            'desc': 'A large chubby 3D character resembling a realistic human anatomy muscle model, visible red muscles with no skin, big protruding belly, exaggerated facial features.',
        },
        'muscle-small': {
            'name': 'Small Muscle Guy',
            'desc': 'A small slim 3D character resembling a realistic human anatomy muscle model, visible red muscles with no skin, athletic build, energetic intense expression.',
        },
        'angry-emoji': {
            'name': 'Angry Emoji',
            'desc': 'A round yellow-orange 3D character resembling an angry emoji face, large expressive eyes, thick furrowed eyebrows, wide open mouth, realistic skin-like texture on smooth round head.',
        },
        'emoji-and-boy': {
            'name': 'Emoji and Boy',
            'desc': 'A small round yellow-orange angry emoji character next to a cute chubby Pixar-style boy with brown hair. The emoji is lecturing the boy.',
        },
    }

    scene_details = {
        'gym': 'modern gym interior with metal equipment, overhead fluorescent lighting, rubber floor',
        'kitchen': 'warm cozy kitchen, wooden table, morning sunlight through window, homey atmosphere',
        'bedroom': 'bedroom with messy bed, warm dim lighting, morning atmosphere, curtains partially open',
        'living-room': 'modern living room, natural daylight, clean interior, soft ambient lighting',
    }

    expression_details = {
        'rage': 'extremely angry expression, veins popping, face turning deep red, mouth wide open screaming',
        'frustrated': 'frustrated annoyed expression, gritting teeth, furrowed brows, twitching eye',
        'shocked': 'shocked wide-eyed expression, jaw dropped, eyebrows raised high',
        'lecturing': 'stern lecturing expression, pointing finger, serious narrowed eyes, slight frown',
        'realization': 'sudden realization expression, eyes lighting up, mouth forming an O shape',
        'excited': 'huge excited grin, sparkling eyes, both fists raised, bouncing with energy',
    }

    char_info = character_details.get(character, character_details['muscle-duo'])
    scene_env = scene_details.get(scene, scene_details['gym'])
    expr = expression_details.get(expression, expression_details['rage'])

    image_prompt = f"""{char_info['desc']}

EXPRESSION: {expr}
ENVIRONMENT: {scene_env}
STYLE: Pixar-style 3D rendering, highly detailed muscle fiber texture, subsurface scattering, dramatic lighting, high contrast, vertical 9:16 format, octane render, 8k, cinematic"""

    # 動画プロンプト
    video_sections = []
    video_sections.append(f"""SCENE: {char_info['name']} character animation
{char_info['desc']}
The character talks directly to camera with {expr}.
Exaggerated facial expressions, mouth moving while speaking, hands gesturing emphatically.""")

    if dialogue:
        dialogue_en = translate_to_english(dialogue)
        video_sections.append(f"""DIALOGUE: "{dialogue_en}"
The character delivers this line with intense emotion and dramatic body language.""")

    if additional_direction:
        direction_en = translate_to_english(additional_direction)
        video_sections.append(f"""ADDITIONAL DIRECTION: {direction_en}""")

    video_sections.append(f"""ENVIRONMENT: {scene_env}
CAMERA: Close-up shots of exaggerated facial expressions, slight camera shake for intensity
STYLE: Pixar-quality 3D animation, dramatic lighting, comedic educational tone, vertical 9:16 format
Keywords: muscle anatomy character, {expression}, educational comedy, Pixar-style, dramatic lighting, 9:16 vertical""")

    return image_prompt.strip(), "\n\n".join(video_sections).strip()


def generate_shizuka_bottle_prompts(form_data):
    """しずかボトルキャラクター用のプロンプトを生成"""
    expression = form_data.get('shizuka_expression', 'friendly')
    scene = form_data.get('shizuka_scene', 'coral-reef')
    direction = form_data.get('shizuka_direction', 'talking')
    dialogue = form_data.get('dialogue', '').strip()
    additional_direction = form_data.get('additional_direction', '').strip()

    expression_details = {
        'friendly': 'warm friendly smile, eyes slightly squinted with joy',
        'surprised': 'eyes wide open, mouth in O shape, both hands on cheeks in surprise',
        'confident': 'confident smirk, one hand on hip, slight head tilt',
        'serious': 'stern serious expression, one finger raised, furrowed brows',
        'excited': 'huge excited grin, sparkling eyes, both fists raised in celebration',
        'wink': 'one eye winking, playful smile, pointing at camera',
    }

    scene_details = {
        'coral-reef': 'beautiful underwater coral reef with colorful corals (pink, purple, orange), tropical fish, floating bubbles, soft blue-green ocean lighting with god rays from above',
        'mountain-spring': 'crystal clear mountain spring, smooth rocks, lush green moss, sunlight filtering through trees, pristine water streams',
        'ice-cave': 'inside a beautiful ice cave, transparent blue ice walls, frost particles floating, cold blue atmospheric lighting',
        'kitchen': 'bright modern kitchen, morning sunlight through window, clean white counter, fresh wholesome atmosphere',
    }

    direction_details = {
        'talking': 'talks calmly with warm smile, one hand raised in greeting, gentle swaying motion',
        'shocking': 'eyes go wide with shock, leans back dramatically, then leans forward pointing at camera urgently',
        'explaining': 'nods confidently while talking, one hand on hip, other hand counting on fingers',
        'deal': 'jumps up excitedly, arms spread wide, huge smile, bouncing with enthusiasm',
        'cta': 'leans close to camera, winks one eye, points at viewer with friendly inviting gesture',
    }

    expr = expression_details.get(expression, expression_details['friendly'])
    scene_env = scene_details.get(scene, scene_details['coral-reef'])
    dir_desc = direction_details.get(direction, direction_details['talking'])

    image_prompt = f"""A cute Pixar-style 3D anthropomorphic water bottle character.

BOTTLE DESIGN (must be exact):
- Clear transparent plastic 500ml water bottle body showing pure water inside
- White screw cap on top
- Label on the center of the bottle with:
  - A large blue water droplet shape in the center of the label
  - Japanese text "しずか" written prominently on the label
  - Smaller text "自然が育てた日本の水" below the droplet
  - Text "500ml" at the bottom of the label
- The bottle has horizontal ridges/grooves on the lower half

CHARACTER FEATURES (add to the bottle):
- Two large cute cartoon eyes with white sclera and black pupils, placed above the label
- A small expressive cartoon mouth below the label
- Two small white-gloved cartoon hands on the left and right sides of the bottle

EXPRESSION: {expr}
ENVIRONMENT: {scene_env}
STYLE: Pixar/Disney-style 3D rendering, adorable product mascot, vertical 9:16 format, highly detailed, octane render, 8k, cinematic
TEXT RENDERING: The label MUST display the Japanese hiragana text「しずか」(shi-zu-ka, 3 characters: し ず か) clearly and correctly. This is the product name and must be the most prominent text on the label. Do NOT misspell or alter these characters."""

    # 動画プロンプト
    video_sections = []
    video_sections.append(f"""SCENE: Shizuka water bottle character animation
A cute anthropomorphic clear water bottle with white cap, blue water droplet logo label, and white-gloved hands.
The character {dir_desc}.
Eyes blink naturally, mouth moves with talking motion.
Water inside the transparent body subtly sloshes with each movement.""")

    if dialogue:
        dialogue_en = translate_to_english(dialogue)
        video_sections.append(f"""DIALOGUE: "{dialogue_en}"
The bottle character delivers this line with expressive gestures and natural body language.""")

    if additional_direction:
        direction_en = translate_to_english(additional_direction)
        video_sections.append(f"""ADDITIONAL DIRECTION: {direction_en}""")

    video_sections.append(f"""ENVIRONMENT: {scene_env}
Bubbles rise continuously, small fish swim past, coral/plants sway gently.
CAMERA: Medium close-up, slight gentle movement
STYLE: Pixar-quality 3D animation, soft underwater lighting, friendly educational tone, vertical 9:16 format
Keywords: water bottle mascot, product animation, cute character, underwater, Pixar-style, 9:16 vertical""")

    return image_prompt.strip(), "\n\n".join(video_sections).strip()


def generate_skeleton_prompts(form_data):
    """
    ガイコツキャラクター用のプロンプトを生成
    感情的なストーリーテリングに特化
    """
    # フォームデータ取得
    scene_setting = form_data.get('character_subject', '')  # character_subjectをシーン設定として使用
    dialogue = form_data.get('dialogue', '').strip()
    additional_direction = form_data.get('additional_direction', '').strip()
    character_emotion = form_data.get('character_emotion', 'panicked and terrified')
    visual_style = form_data.get('visual_style', 'grotesque comedy, Pixar meets body horror')

    # 感情に基づいた動作を生成
    emotion_actions = {
        'panicked and terrified': {
            'posture': 'hunched forward with shoulders raised defensively, hands gripping head or covering face',
            'movement': 'trembling violently, occasional flinching movements, rapid shallow breathing',
            'eyes': 'eyes wide open in terror, pupils dilated, rapid eye movements scanning surroundings'
        },
        'desperate and pleading': {
            'posture': 'reaching forward with outstretched arms, body leaning forward desperately',
            'movement': 'hands clasped together in pleading gesture, body rocking slightly',
            'eyes': 'eyes watery and desperate, intense focus, eyebrows raised in plea'
        },
        'crying and sobbing loudly': {
            'posture': 'collapsed inward, elbows on knees, hands clutching head',
            'movement': 'shoulders shaking with sobs, occasional convulsive movements, body trembling',
            'eyes': 'tears streaming continuously, eyes squeezed shut or half-open in anguish'
        },
        'angrily shouting': {
            'posture': 'leaning forward aggressively, fists clenched, body tense and ready',
            'movement': 'sharp jabbing motions with arms, aggressive gestures, body vibrating with rage',
            'eyes': 'eyes narrowed in fury, intense glare, eyebrows furrowed deeply'
        },
        'exhausted and tired': {
            'posture': 'slumped forward, head hanging down, arms hanging limply',
            'movement': 'slow labored breathing, occasional slumping further, minimal energy',
            'eyes': 'half-closed eyes, vacant stare, slow blinking'
        },
        'relieved and comfortable': {
            'posture': 'relaxed shoulders, body leaning back comfortably, open posture',
            'movement': 'deep exhale of relief, gentle swaying, relaxed fluid movements',
            'eyes': 'eyes gently closed or softly gazing, peaceful expression'
        }
    }

    # デフォルトのアクション
    action_details = emotion_actions.get(character_emotion, emotion_actions['panicked and terrified'])

    # 画像生成プロンプト（ベース画像用）
    image_prompt = f"""A chibi-style 4-head-tall skeleton character in a photorealistic environment.

CHARACTER DESIGN:
- Chibi proportions: 4 heads tall with oversized head and small body
- Beige/cream colored bones with realistic bone texture
- Large cartoonish eyes with realistic pupils showing {character_emotion} emotion
- Full skeletal anatomy: visible ribcage, spine, pelvis
- Small arms and legs with defined joints
- Long tongue hanging out slightly
- Expressive facial features despite being a skeleton

ENVIRONMENT:
- {scene_setting}
- Photorealistic background with dramatic lighting
- 3D character integrated into realistic setting
- Rich environmental details and atmosphere

POSE & EXPRESSION:
- {action_details['posture']}
- Facial expression showing {character_emotion}
- {action_details['eyes']}

STYLE:
- High-quality 3D render
- Pixar-style character design
- Photorealistic environment
- Dramatic cinematic lighting
- Vertical 9:16 portrait orientation
- Professional animation-ready character

NO TEXT, NO WORDS, NO LETTERS in the image"""

    # 動画生成プロンプト（アニメーション用）
    video_sections = []

    # キャラクターデザイン参照
    video_sections.append(f"""A chibi-style 4-head-tall skeleton character, matching the provided character design.

The character is in: {scene_setting}""")

    # 追加演出指示を最優先で配置
    if additional_direction:
        additional_en = translate_to_english(additional_direction)
        video_sections.append(f"""🔴 CRITICAL REQUIREMENT - MUST IMPLEMENT THIS EXACTLY:
{additional_en}

This direction is the HIGHEST PRIORITY and must be clearly visible throughout the entire animation.""")

    # 現在の状態とアクション
    if dialogue:
        video_sections.append(f"""The character is experiencing {character_emotion} emotion and expresses: "{dialogue}"

The character's expressions and body language powerfully convey this emotion.
NO text overlays or subtitles should appear in the video.""")
    else:
        video_sections.append(f"""The character is experiencing {character_emotion} emotion through powerful body language.""")

    # 詳細な姿勢とボディランゲージ
    body_language_text = f"""POSTURE & BODY LANGUAGE:
{action_details['posture']}

MOVEMENT DETAILS:
{action_details['movement']}

FACIAL EXPRESSION:
{action_details['eyes']}
The long tongue hangs downward, swaying with breath and emotion."""

    # 追加演出指示がある場合は統合
    if additional_direction:
        body_language_text += f"\n\n⚠️ CRITICAL: All movements must incorporate: {translate_to_english(additional_direction)}"

    video_sections.append(body_language_text)

    # 環境の詳細
    scene_description = translate_to_english(scene_setting) if scene_setting else "dramatic environment"
    video_sections.append(f"""ENVIRONMENT:
{scene_description}
The setting enhances the emotional narrative.
Dramatic lighting isolates the character.
Environmental details are clearly readable and support the storytelling.""")

    # シネマティック指示
    video_sections.append(f"""CINEMATOGRAPHY:
High-quality 3D animation with Pixar-style emotional acting.
Strong readable posing and clear storytelling.
Camera slowly pushes in, focusing on the character's emotional state.
Lighting emphasizes the drama and mood.
Vertical 9:16 format.""")

    # キーワード
    emotion_keywords = character_emotion.replace(' and ', ', ')
    video_sections.append(f"""Keywords: chibi skeleton, {emotion_keywords}, emotional storytelling, Pixar-style animation, dramatic lighting, clear narrative, cinematic composition, 9:16 vertical format""")

    video_prompt = "\n\n".join(video_sections)

    return image_prompt, video_prompt


def generate_dog_prompts(form_data):
    """
    わんこキャラクター用のプロンプトを生成
    3DCGアニメーション風のかわいい犬キャラクター
    """
    # フォームデータ取得
    dog_breed = form_data.get('dog_breed', 'pomeranian')
    dog_scene = form_data.get('dog_scene', 'living-room')
    dog_action = form_data.get('dog_action', 'smiling-camera')
    dialogue = form_data.get('dialogue', '').strip()
    additional_direction = form_data.get('additional_direction', '').strip()
    character_emotion = form_data.get('character_emotion', 'happy and grateful')

    # 犬種の特徴マッピング
    breed_details = {
        'pomeranian': {
            'name': 'Pomeranian',
            'description': 'fluffy orange-cream colored fur, small fox-like face, pointy ears, thick double coat',
            'size': 'tiny',
            'personality': 'energetic and playful'
        },
        'chihuahua': {
            'name': 'Chihuahua',
            'description': 'brown and tan colored, large pointed ears, big expressive eyes, smooth short coat',
            'size': 'very small',
            'personality': 'alert and confident'
        },
        'shiba': {
            'name': 'Shiba Inu',
            'description': 'fox-like appearance, orange-red coat with white markings, curled tail, triangular ears',
            'size': 'small to medium',
            'personality': 'bold and spirited'
        },
        'toy-poodle': {
            'name': 'Toy Poodle',
            'description': 'curly fluffy coat, elegant proportions, round eyes, floppy ears',
            'size': 'tiny',
            'personality': 'intelligent and cheerful'
        },
        'french-bulldog': {
            'name': 'French Bulldog',
            'description': 'bat-like ears, wrinkled face, compact muscular body, short smooth coat',
            'size': 'small',
            'personality': 'playful and affectionate'
        },
        'corgi': {
            'name': 'Corgi',
            'description': 'short legs, long body, fox-like face, large upright ears, fluffy coat',
            'size': 'small to medium',
            'personality': 'friendly and outgoing'
        },
        'golden-retriever': {
            'name': 'Golden Retriever',
            'description': 'golden flowing coat, friendly face, floppy ears, gentle eyes',
            'size': 'medium to large',
            'personality': 'friendly and devoted'
        },
        'dachshund': {
            'name': 'Dachshund',
            'description': 'long body, short legs, long floppy ears, expressive face',
            'size': 'small',
            'personality': 'clever and lively'
        }
    }

    # シーン環境マッピング
    scene_details = {
        'living-room': 'cozy living room with sofa, cushions, warm lighting, plants, and homey atmosphere',
        'entrance': 'home entrance with door, coat rack, welcome mat, natural light from outside',
        'sofa': 'comfortable sofa with soft cushions, throw blankets, warm ambient lighting',
        'garden': 'beautiful garden with green grass, flowers, trees, sunshine',
        'park': 'sunny park with trees, walking path, benches, blue sky',
        'cafe': 'cozy cafe interior with wooden tables, warm lighting, peaceful atmosphere',
        'bedroom': 'comfortable bedroom with bed, pillows, soft lighting, relaxing mood',
        'window': 'window area with curtains, natural sunlight streaming in, peaceful view'
    }

    # アクション・表情マッピング
    action_details = {
        'smiling-camera': 'looking directly at camera with big happy smile, mouth slightly open showing happiness, tail wagging gently, eyes sparkling with joy',
        'head-tilt': 'tilting head to one side curiously, ears perked up, eyes wide and curious, adorable questioning expression',
        'tail-wag': 'wagging tail enthusiastically from side to side, body wiggling with excitement, happy expression',
        'running': 'running energetically toward camera, legs moving in playful motion, ears bouncing, joyful expression',
        'sitting': 'sitting in perfect position, chest out proudly, tail curled around body, looking up attentively',
        'jumping': 'jumping up and down with excitement, all four paws off ground, ears flying up, pure joy on face',
        'sleeping': 'curled up sleepily, eyes half-closed or gently closing, peaceful relaxed expression, breathing slowly',
        'playing': 'playing with toy, paws batting playfully, focused concentration mixed with joy, playful movements',
        'curious': 'staring intently with wide curious eyes, head slightly forward, ears perked, investigating something interesting'
    }

    breed_info = breed_details.get(dog_breed, breed_details['pomeranian'])
    scene_env = scene_details.get(dog_scene, scene_details['living-room'])
    action_desc = action_details.get(dog_action, action_details['smiling-camera'])

    # 画像生成プロンプト
    image_prompt = f"""A cute 3D animated {breed_info['name']} dog character in Pixar/Disney animation style.

CHARACTER DESIGN:
- Adorable {breed_info['size']} {breed_info['name']} puppy
- {breed_info['description']}
- Oversized expressive eyes with realistic reflections and emotional depth
- Smooth 3D rendered fur with realistic texture and lighting
- Cute proportions with slightly enlarged head for kawaii appeal
- {breed_info['personality']} personality showing in expression
- {action_desc}

ENVIRONMENT:
- Photorealistic {scene_env}
- Cinematic lighting with warm tones
- Shallow depth of field focusing on the dog
- Rich environmental details
- Professional 3D rendering quality

STYLE:
- High-quality 3D CGI animation (Pixar/Disney level)
- Realistic fur simulation and lighting
- Photorealistic background integrated with stylized character
- Vertical 9:16 portrait format for social media
- Warm, inviting, heartwarming mood
- Professional render quality with ray tracing

The dog should be incredibly cute and endearing, capturing the essence of {breed_info['name']} charm.

NO TEXT, NO WORDS, NO LETTERS in the image"""

    # 動画生成プロンプト
    video_sections = []

    video_sections.append(f"""A 3D animated {breed_info['name']} puppy character in Pixar/Disney style, matching the provided character design.

The puppy is in: {scene_env}""")

    # 追加演出指示を最優先で配置
    if additional_direction:
        additional_en = translate_to_english(additional_direction)
        video_sections.append(f"""🔴 CRITICAL REQUIREMENT - MUST IMPLEMENT THIS EXACTLY:
{additional_en}

This direction is the HIGHEST PRIORITY and must be clearly visible throughout the entire animation.""")

    if dialogue:
        video_sections.append(f"""The adorable {breed_info['name']} puppy expresses the emotion: "{dialogue}"

The puppy's expressions and body language convey this feeling through movements, facial expressions, and gestures.
NO text overlays or subtitles should appear in the video.""")
    else:
        video_sections.append(f"""The {breed_info['name']} puppy communicates through expressive body language and facial expressions.""")

    animation_text = f"""CHARACTER ANIMATION:
{action_desc}

The puppy's movements are fluid and natural:
- Realistic fur physics and movement
- Breathing animation (chest rising and falling gently)
- Subtle ear twitches and movements
- Eye blinks and micro-expressions
- Natural weight and balance in poses

Pixar-level character animation with appeal and personality."""

    # 追加演出指示がある場合は統合
    if additional_direction:
        animation_text += f"\n\n⚠️ CRITICAL: All animations must incorporate: {translate_to_english(additional_direction)}"

    video_sections.append(animation_text)

    video_sections.append(f"""ENVIRONMENT & CINEMATOGRAPHY:
{scene_env}

Photorealistic background with:
- Cinematic lighting and atmosphere
- Warm color grading
- Shallow depth of field keeping focus on the puppy
- Subtle camera movement (slow push-in or gentle tracking)
- Professional compositing of 3D character with environment

Vertical 9:16 format optimized for TikTok/social media.""")

    video_sections.append(f"""Keywords: cute {breed_info['name']}, 3D animation, Pixar style, adorable puppy, photorealistic environment, heartwarming, kawaii, vertical video, social media optimized, professional CGI""")

    video_prompt = "\n\n".join(video_sections)

    return image_prompt, video_prompt


def generate_cat_prompts(form_data):
    """
    ニャンコキャラクター用のプロンプトを生成
    3DCGアニメーション風のかわいい猫キャラクター
    """
    # フォームデータ取得
    cat_breed = form_data.get('cat_breed', 'gray-tabby')
    cat_scene = form_data.get('cat_scene', 'living-room')
    cat_action = form_data.get('cat_action', 'staring-camera')
    dialogue = form_data.get('dialogue', '').strip()
    additional_direction = form_data.get('additional_direction', '').strip()
    character_emotion = form_data.get('character_emotion', 'curious and intrigued')

    # 猫種の特徴マッピング
    breed_details = {
        'gray-tabby': {
            'name': 'Gray Tabby',
            'description': 'gray striped tabby pattern, silver-gray fur with dark stripes, green or amber eyes',
            'personality': 'playful and curious'
        },
        'orange-tabby': {
            'name': 'Orange Tabby',
            'description': 'orange-cream colored with darker orange stripes, warm ginger fur, bright amber eyes',
            'personality': 'friendly and outgoing'
        },
        'calico': {
            'name': 'Calico',
            'description': 'tri-color pattern with white, orange, and black patches, distinctive colorful coat',
            'personality': 'independent and spirited'
        },
        'black': {
            'name': 'Black Cat',
            'description': 'sleek pure black fur, bright yellow or green eyes, elegant silhouette',
            'personality': 'mysterious and affectionate'
        },
        'white': {
            'name': 'White Cat',
            'description': 'pure white fluffy fur, blue or heterochromatic eyes, angelic appearance',
            'personality': 'gentle and calm'
        },
        'scottish-fold': {
            'name': 'Scottish Fold',
            'description': 'folded ears, round face, soft plush coat, adorable owl-like appearance',
            'personality': 'sweet and gentle'
        },
        'persian': {
            'name': 'Persian',
            'description': 'long fluffy coat, flat face, round eyes, luxurious fur',
            'personality': 'calm and regal'
        },
        'ragdoll': {
            'name': 'Ragdoll',
            'description': 'blue eyes, color-point pattern, silky semi-long fur, large and fluffy',
            'personality': 'docile and relaxed'
        },
        'siamese': {
            'name': 'Siamese',
            'description': 'cream body with dark points on face, ears, paws, and tail, striking blue almond eyes',
            'personality': 'vocal and social'
        }
    }

    # シーン環境マッピング
    scene_details = {
        'living-room': 'cozy living room with sofa, warm lighting, comfortable atmosphere',
        'window-sill': 'sunny window sill with curtains, natural light streaming in, peaceful view outside',
        'sofa': 'soft comfortable sofa with cushions, cozy blanket, warm ambient lighting',
        'cardboard-box': 'inside a cardboard box, playful hiding spot, cozy confined space',
        'cat-tower': 'cat tower with multiple levels, scratching posts, elevated perch',
        'bed': 'comfortable bed with soft blankets and pillows, relaxing sleeping area',
        'clouds': 'floating on fluffy white clouds in dreamy pastel sky, magical fantasy atmosphere',
        'garden': 'beautiful garden with flowers, green grass, butterflies, sunshine',
        'cafe': 'cozy cafe interior with wooden furniture, warm lighting, peaceful atmosphere'
    }

    # アクション・表情マッピング
    action_details = {
        'staring-camera': 'looking directly at camera with big round eyes, intense curious gaze, slight head tilt, mesmerizing stare',
        'head-tilt': 'tilting head to one side adorably, ears perked up, curious questioning expression, innocent look',
        'meowing': 'mouth open in adorable meow, expressive face, communicating vocally, endearing expression',
        'stretching': 'stretching body with front paws extended forward, back arched, yawning contentedly, relaxed pose',
        'grooming': 'licking paw and grooming face, tongue out slightly, focused concentration, calm and clean',
        'playing': 'playing with toy, paws batting playfully, alert and energetic, hunter instincts showing',
        'sleeping': 'curled up sleeping peacefully, eyes closed, gentle breathing, utterly relaxed and content',
        'curious': 'ears forward, eyes wide with curiosity, investigating something interesting, alert and engaged',
        'lazy': 'lounging lazily, half-closed eyes, completely relaxed, content and peaceful expression',
        'paw-licking': 'licking front paw elegantly, grooming ritual, refined and graceful movement'
    }

    breed_info = breed_details.get(cat_breed, breed_details['gray-tabby'])
    scene_env = scene_details.get(cat_scene, scene_details['living-room'])
    action_desc = action_details.get(cat_action, action_details['staring-camera'])

    # 画像生成プロンプト
    image_prompt = f"""A cute 3D animated {breed_info['name']} kitten character in Pixar/Disney animation style.

CHARACTER DESIGN:
- Adorable {breed_info['name']} kitten
- {breed_info['description']}
- Oversized expressive eyes with realistic reflections and emotional depth
- Smooth 3D rendered fur with realistic texture and lighting
- Cute proportions with slightly enlarged head for maximum cuteness
- {breed_info['personality']} personality showing in expression
- {action_desc}

ENVIRONMENT:
- Photorealistic {scene_env}
- Cinematic lighting with warm tones
- Shallow depth of field focusing on the kitten
- Rich environmental details
- Professional 3D rendering quality

STYLE:
- High-quality 3D CGI animation (Pixar/Disney level)
- Realistic fur simulation and lighting
- Photorealistic background integrated with stylized character
- Vertical 9:16 portrait format for social media
- Warm, heartwarming, adorable mood
- Professional render quality with ray tracing

The kitten should be irresistibly cute and endearing, capturing the essence of {breed_info['name']} charm.

NO TEXT, NO WORDS, NO LETTERS in the image"""

    # 動画生成プロンプト
    video_sections = []

    video_sections.append(f"""A 3D animated {breed_info['name']} kitten character in Pixar/Disney style, matching the provided character design.

The kitten is in: {scene_env}""")

    # 追加演出指示を最優先で配置
    if additional_direction:
        additional_en = translate_to_english(additional_direction)
        video_sections.append(f"""🔴 CRITICAL REQUIREMENT - MUST IMPLEMENT THIS EXACTLY:
{additional_en}

This direction is the HIGHEST PRIORITY and must be clearly visible throughout the entire animation.""")

    if dialogue:
        video_sections.append(f"""The adorable {breed_info['name']} kitten expresses the emotion: "{dialogue}"

The kitten's expressions and body language convey this feeling through movements, facial expressions, and gestures.
NO text overlays or subtitles should appear in the video.""")
    else:
        video_sections.append(f"""The {breed_info['name']} kitten communicates through expressive body language and facial expressions.""")

    animation_text = f"""CHARACTER ANIMATION:
{action_desc}

The kitten's movements are fluid and natural:
- Realistic fur physics and movement
- Gentle breathing animation
- Subtle ear movements and whisker twitches
- Eye blinks and micro-expressions
- Natural feline grace and balance

Pixar-level character animation with maximum cuteness and appeal."""

    # 追加演出指示がある場合は統合
    if additional_direction:
        animation_text += f"\n\n⚠️ CRITICAL: All animations must incorporate: {translate_to_english(additional_direction)}"

    video_sections.append(animation_text)

    video_sections.append(f"""ENVIRONMENT & CINEMATOGRAPHY:
{scene_env}

Photorealistic background with:
- Cinematic lighting and atmosphere
- Warm color grading
- Shallow depth of field keeping focus on the kitten
- Subtle camera movement (slow push-in or gentle tracking)
- Professional compositing of 3D character with environment

Vertical 9:16 format optimized for TikTok/social media.""")

    video_sections.append(f"""Keywords: cute {breed_info['name']}, 3D animation, Pixar style, adorable kitten, photorealistic environment, heartwarming, kawaii, vertical video, social media optimized, professional CGI""")

    video_prompt = "\n\n".join(video_sections)

    return image_prompt, video_prompt


def generate_nanobanana_object_prompts(form_data):
    """
    ライフハッくん（モノ）用のプロンプトを生成
    日常のモノをキャラクター化
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
    dialogue_en = dialogue if dialogue else ''
    additional_direction_en = translate_to_english(additional_direction) if additional_direction else ''

    # モノの環境を設定（日常空間）
    object_environments = {
        'ペットボトル': 'on a desk or table in daily life setting',
        'リモコン': 'on a sofa or coffee table in living room',
        'スマホ': 'on a desk or in hand, modern lifestyle setting',
        '消しゴム': 'on a study desk with notebooks and pencils',
        'お菓子': 'on a table or in pantry, snack time setting',
        'ボールペン': 'on an office desk with papers',
        '財布': 'on a table or in bag, daily carry setting'
    }

    # デフォルト環境（日常の机や部屋）
    environment = object_environments.get(character_subject, 'on a surface in everyday life setting, living space or workspace')

    # Nano Banana プロンプト（モノ版）
    nano_banana_prompt = f"""An anthropomorphized {character_subject_en} object character - literally a {character_subject_en} transformed into a cute character with a face.

CHARACTER DETAILS:
- The character IS a {character_subject_en} with cartoon features added
- Body shape and structure based on actual {character_subject_en} appearance
- Maintains recognizable {character_subject_en} characteristics and colors
- Tiny object body with adorable cartoon modifications

FACIAL FEATURES (CRITICAL):
- HUGE bulging expressive eyes (anime-style, NOT realistic)
- Wide open mouth showing expression
- Clear defined facial features with personality
- Exaggerated {character_emotion} expression
- NOT a photorealistic object - this is a CHARACTER with emotions

BODY:
- Small stubby arms and legs added to the {character_subject_en}
- Arms waving expressively
- Cute yet expressive appearance
- Maintains recognizable {character_subject_en} form

ENVIRONMENT:
- Placed in {environment}
- Surrounded by realistic everyday objects and furniture
- {camera_angle} perspective
- Environment contrasts with stylized cartoon character

STYLE:
- 3D rendered in {visual_style} style
- Pixar animation quality character design
- Photorealistic environment setting
- Dramatic lighting with everyday life atmosphere
- Highly detailed, octane render, 8k
- Vertical portrait orientation, 9:16 aspect ratio

NO TEXT, NO WORDS, NO LETTERS in the image"""

    if additional_direction_en:
        nano_banana_prompt += f"\n\nADDITIONAL DIRECTION:\n{additional_direction_en}"

    nano_banana_prompt = nano_banana_prompt.strip()

    # Kling プロンプト（構造化フォーマット - モノ版）
    kling_sections = []

    # Subject
    kling_sections.append(f"""Subject:
An anthropomorphized {character_subject_en} object character - literally a {character_subject_en} transformed into a cartoon creature with a face and personality. The character IS a {character_subject_en} with huge bulging eyes, tiny arms and legs added. This is NOT a generic blob but specifically recognizable as a {character_subject_en}. Standing in {environment}.""")

    # Context
    context_desc = f"The everyday life setting shows a typical environment where {character_subject_en} would normally exist. The atmosphere is relatable and familiar, mixing realistic objects with the cartoon character."

    kling_sections.append(f"""Context:
{context_desc}""")

    # 追加演出指示を最優先で配置
    if additional_direction_en:
        kling_sections.append(f"""🔴 CRITICAL REQUIREMENT - MUST IMPLEMENT THIS EXACTLY:
{additional_direction_en}

This direction is the HIGHEST PRIORITY and must be clearly visible throughout the entire animation.""")

    # Action（セリフあり/なし）
    if dialogue_en:
        lip_sync = generate_lip_sync(dialogue_en)
        has_japanese = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in dialogue_en)

        action_text = f"""Action:
The {character_subject_en} character suddenly reacts with {character_emotion} emotion toward the camera.

The character expresses: {lip_sync}

Character performance:
- Expression matches the emotional tone
- Tiny arms gesture dramatically to emphasize the emotion
- Body language reinforces the meaning and feeling
- NO text overlays, NO subtitles, NO words should appear in the video"""

        if additional_direction_en:
            action_text += f"\n\n⚠️ CRITICAL: All actions must incorporate: {additional_direction_en}"

        kling_sections.append(action_text)
    else:
        action_text = f"""Action:
The {character_subject_en} character shows {character_emotion} emotion through exaggerated body language.

Animation:
- HUGE EYES widening dramatically
- Mouth opening wider in exaggerated expression
- Clear defined facial features with personality
- Small arms and legs flailing expressively
- Body wobbles in rubber-hose cartoon style"""

        if additional_direction_en:
            action_text += f"\n\n⚠️ CRITICAL: All actions must incorporate: {additional_direction_en}"

        kling_sections.append(action_text)

    # Style
    style_desc = "Pixar-style 3D animation"
    if "grotesque" in visual_style:
        style_desc += ", exaggerated cartoon acting, expressive facial animation, comedic humor"
    elif "cute" in visual_style:
        style_desc += ", cute character design, friendly animation, warm colors"

    kling_sections.append(f"""Style:
{style_desc}.""")

    # Camera Movement
    kling_sections.append(f"""Camera Movement:
Dynamic camera movement, slight zoom emphasizing character's reaction, smooth cinematic movement.""")

    # Composition
    kling_sections.append(f"""Composition:
Vertical 9:16 format (portrait orientation).
The {character_subject_en} character in everyday environment, surrounded by realistic objects.""")

    # Ambiance & Effects
    kling_sections.append(f"""Ambiance & Effects:
- Natural lighting from everyday environment
- Realistic object textures in background
- Contrast between cartoon character and photorealistic setting""")

    kling_prompt = "\n\n".join(kling_sections)

    return nano_banana_prompt, kling_prompt.strip()


def generate_prompts(form_data):
    """
    Kling公式フォーマットでプロンプトを生成
    キャラクタータイプに応じて適切な関数を呼び出す
    """
    character_type = form_data.get('character_type', 'nanobanana-body')

    # 筋肉くんの場合
    if character_type == 'kinnikukun':
        return generate_kinnikukun_prompts(form_data)

    # しずかボトルの場合
    if character_type == 'shizuka-bottle':
        return generate_shizuka_bottle_prompts(form_data)

    # ライフハッくん（モノ）の場合
    if character_type == 'nanobanana-object':
        return generate_nanobanana_object_prompts(form_data)

    # ニャンコキャラクターの場合
    if character_type == 'cat':
        return generate_cat_prompts(form_data)

    # わんこキャラクターの場合
    if character_type == 'dog':
        return generate_dog_prompts(form_data)

    # スケルトンキャラクターの場合
    if character_type == 'skeleton':
        return generate_skeleton_prompts(form_data)

    # Nano Bananaキャラクターの場合（従来の処理）
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

    # 追加演出指示を最優先で配置
    if additional_direction_en:
        kling_sections.append(f"""🔴 CRITICAL REQUIREMENT - MUST IMPLEMENT THIS EXACTLY:
{additional_direction_en}

This direction is the HIGHEST PRIORITY and must be clearly visible throughout the entire animation.""")

    # Action（セリフあり/なし）
    if dialogue_en:
        # セリフありの場合
        lip_sync = generate_lip_sync(dialogue_en)

        # 日本語かどうかをチェック
        has_japanese = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in dialogue_en)

        action_text = f"""Action:
The {character_subject_en} character suddenly reacts with {character_emotion} emotion toward the camera.

The character expresses: {lip_sync}

Character performance:
- Expression matches the emotional tone
- Tiny arms gesture dramatically to emphasize the emotion
- Body language reinforces the meaning and feeling

Animation details:
- Eyes vibrate and bulge dramatically to show emotion
- Body wobbles in rubber-hose cartoon style
- Surrounding biological elements (saliva/moisture) react to the emotion
- Character leans forward with intensity
- Facial expressions change naturally
- NO text overlays, NO subtitles, NO words should appear in the video"""

        if additional_direction_en:
            action_text += f"\n\n⚠️ CRITICAL: All actions must incorporate: {additional_direction_en}"

        kling_sections.append(action_text)
    else:
        # セリフなしの場合
        action_text = f"""Action:
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
- Character shows intense emotional reaction"""

        if additional_direction_en:
            action_text += f"\n\n⚠️ CRITICAL: All actions must incorporate: {additional_direction_en}"

        kling_sections.append(action_text)

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


def generate_image_with_imagen_and_reference(prompt, reference_image_b64):
    """Gemini + 参考画像で擬人化キャラ画像を生成"""
    try:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        print(f"\n🎨 Gemini 参考画像付き画像生成開始...")
        print(f"プロンプト: {prompt[:100]}...")

        model = genai.GenerativeModel('gemini-2.5-flash-image')

        # 参考画像をPartとして組み立て
        image_part = {
            'inline_data': {
                'mime_type': 'image/jpeg',
                'data': reference_image_b64
            }
        }

        response = model.generate_content(
            [
                image_part,
                """Add cute cartoon eyes and a small mouth to this bottle.

CRITICAL TEXT RULE: The label on the bottle MUST display the Japanese text「しずか」exactly as written. These are the 3 Japanese hiragana characters: し ず か. Do NOT change, misspell, or omit this text. The text「しずか」must be clearly visible and correctly written on the label.

Do not change anything else about the bottle — keep the shape, cap, transparency, and label layout exactly the same."""
            ],
            generation_config={
                'response_modalities': ['IMAGE', 'TEXT'],
            }
        )

        # 画像データを取得
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_filename = f"generated_image_{timestamp}.png"
                    image_path = OUTPUTS_DIR / image_filename

                    with open(image_path, 'wb') as f:
                        f.write(image_data)

                    print(f"✅ 参考画像付き画像生成完了: {image_filename}")

                    return {
                        'success': True,
                        'image_path': str(image_path),
                        'image_filename': image_filename,
                        'image_url': f'/outputs/{image_filename}'
                    }

        # 画像が返ってこなかった場合、通常のImagen生成にフォールバック
        print("⚠️ Gemini画像生成失敗、Imagenにフォールバック")
        return generate_image_with_imagen(prompt)

    except Exception as e:
        print(f"❌ Gemini参考画像生成エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        # フォールバック
        print("⚠️ Imagenにフォールバック")
        return generate_image_with_imagen(prompt)


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

        # セリフがある場合でもテロップは表示しない
        # キャラクターの表情とボディランゲージのみで表現
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
            # 安全フィルターチェック
            rai_filtered_count = result['generateVideoResponse'].get('raiMediaFilteredCount', 0)
            if rai_filtered_count > 0:
                reasons = result['generateVideoResponse'].get('raiMediaFilteredReasons', [])
                reason_text = reasons[0] if reasons else '不明な理由'
                raise Exception(f"動画生成が安全フィルターによりブロックされました。\n理由: {reason_text}\n\nヒント: セリフを削除するか、より穏やかな表現に変更してみてください。")

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
        reference_image = data.get('reference_image')  # base64画像データ

        if not prompt:
            return jsonify({'success': False, 'error': 'プロンプトが必要です'}), 400

        if not GOOGLE_API_KEY:
            return jsonify({'success': False, 'error': 'Google API Keyが設定されていません'}), 500

        # 参考画像がある場合、Geminiで参考画像ベースの生成
        if reference_image:
            result = generate_image_with_imagen_and_reference(prompt, reference_image)
        else:
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
