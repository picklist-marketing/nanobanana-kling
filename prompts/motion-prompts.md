# Kling AI モーションプロンプト集

Nano Bananaで生成した静止画を、Klingで動画化する際のモーションプロンプト例集

---

## 📋 基本構造

Klingでは、画像アップロード後に「モーションプロンプト」を追加することで動きを制御できます。

```
[カメラの動き] + [キャラクターの動き] + [環境/エフェクトの動き] + [雰囲気/スタイル]
```

---

## 🎬 キャラクター表情・動き系

### 基本的な表情変化

#### 笑顔になる
```
The character slowly smiles, eyes lighting up with joy,
slight head tilt, hair gently swaying,
smooth natural animation, subtle breathing motion
```

#### まばたき・自然な動作
```
Character blinks naturally, subtle facial expressions,
gentle breathing motion, hair flowing softly in the breeze,
natural idle animation
```

#### 驚く
```
Eyes widen in surprise, mouth opens slightly,
quick head movement backward,
hair bounces with the motion,
dynamic reaction animation
```

#### ウインク
```
Character winks playfully, slight smile,
one eye closes smoothly,
small head tilt, cheerful expression
```

---

## 📸 カメラワーク系

### ズーム系

#### スローズームイン
```
Slow zoom in towards character's face,
maintaining focus on eyes,
cinematic depth of field, smooth camera movement
```

#### ドラマチックズームアウト
```
Dramatic zoom out revealing full scene,
character remains centered,
epic reveal, cinematic camera pull-back
```

#### ダイナミックプッシュイン
```
Fast push-in towards character with slight rotation,
intense focus, dynamic camera movement,
cinematic impact
```

### 回転系

#### 周回（オービット）
```
Camera slowly orbits around the character 360 degrees,
character stays in focus, smooth rotation,
cinematic circular movement
```

#### 部分回転
```
Camera rotates 45 degrees around character,
revealing side profile, smooth arc movement,
elegant camera work
```

### パン・ティルト系

#### 上下パン
```
Camera pans up from feet to face,
revealing character gradually,
smooth vertical movement, cinematic reveal
```

#### 左右パン
```
Camera pans from left to right across the scene,
following character's gaze, smooth horizontal movement
```

---

## 🌟 環境・エフェクト系

### 光・パーティクル系

#### きらきらエフェクト
```
Magical sparkles and light particles floating around character,
glowing effects intensifying, gentle movement,
dreamy atmosphere, bokeh background shimmer
```

#### 光の変化
```
Lighting gradually shifts from warm to cool tones,
shadows moving subtly, atmospheric lighting changes,
cinematic color grading transition
```

#### 風エフェクト
```
Strong wind effect, hair and clothes flowing dramatically,
particles and leaves blowing across the scene,
dynamic environmental movement
```

### 背景系

#### 背景ボケ変化
```
Background gradually blurs with bokeh effect,
character remains sharp in focus,
depth of field transition, cinematic look
```

#### 背景スクロール
```
Background slowly scrolls with parallax effect,
character stays centered,
depth and movement in environment
```

---

## 🎭 シーン・雰囲気別プロンプト

### 日常系・優しい雰囲気

#### 穏やかな風景
```
Gentle breeze, character's hair flowing softly,
peaceful expression with subtle smile appearing,
warm sunlight particles floating,
background slightly defocuses with bokeh,
calm and serene atmosphere
```

#### 朝の目覚め
```
Character slowly opens eyes, gentle blink,
slight head turn looking around,
morning sunlight gradually brightening,
peaceful awakening animation
```

---

### アクション系・ダイナミック

#### 戦闘準備
```
Character's eyes glow brighter, intense focused expression,
energy particles gathering around,
hair whipping in power surge,
camera slight shake for impact,
epic battle-ready atmosphere
```

#### パワー発動
```
Energy aura expanding from character,
eyes glowing intensely, hair floating upward,
dramatic lighting changes with power-up effects,
camera slow zoom with rotation,
powerful transformation scene
```

---

### ファンタジー・魔法系

#### 魔法詠唱
```
Character's lips moving slightly as if chanting,
magical runes and circles appearing and rotating around,
glowing particles swirling,
mystical energy building up,
ethereal atmosphere with volumetric lighting
```

#### 妖精の舞
```
Character floating gently up and down,
wings fluttering softly,
magical particles trailing movement,
dreamy slow-motion effect,
enchanted forest ambiance
```

---

### コミカル・面白系（提供画像風）

#### 驚愕リアクション
```
Eyes bulging out cartoonishly,
mouth opening wider in exaggerated shock,
quick head shake or bounce,
impact lines and comic effects appearing,
over-the-top anime reaction
```

#### 怒りプルプル
```
Character vibrating with anger,
steam particles rising from head,
face turning slightly red,
comic anger effects pulsing,
cartoonish exaggerated emotion
```

#### ジト目
```
Eyes slowly narrowing into skeptical look,
slight head tilt, one eyebrow raising,
comedic timing, subtle judgmental expression
```

---

### 感動・エモーショナル系

#### 涙
```
Single tear forming and rolling down cheek,
eyes glistening with emotion,
slight lip tremble, soft ambient lighting,
emotional atmosphere
```

#### 希望の光
```
Character looking up with hopeful expression,
soft smile appearing, eyes reflecting light,
warm golden rays breaking through,
inspiring uplifting moment
```

---

## 🎨 スタイル・品質指定

### 基本品質タグ（Klingで使用）
```
cinematic, smooth animation, high quality, 4k,
natural motion, photorealistic, coherent movement
```

### アニメスタイル特化
```
anime-style movement, expressive animation,
dynamic motion, vibrant, studio-quality animation
```

### リアル寄り
```
photorealistic motion, natural physics,
realistic lighting changes, subtle movements,
lifelike animation
```

---

## ⚙️ Kling設定の推奨値

### 動画尺
- **5秒**: クイックなリアクション、シンプルな動き
- **10秒**: 標準的なシーン、複数の動き要素
- **15-30秒**: 複雑なシーン、ストーリー性

### 解像度
- **1080p (推奨)**: バランスが良い、SNS投稿に最適
- **720p**: 速度重視、テスト用
- **4K**: 最高品質、展示用

### カメラモーション強度
- **弱**: 静的な雰囲気、キャラクター動きメイン
- **中（推奨）**: バランスの良い動き
- **強**: ダイナミックなMV風

---

## 📱 クイック生成用ショートプロンプト

時間がない時用の簡潔版

### パターン1: シンプル笑顔
```
Character smiles naturally, gentle blink,
hair flows softly, smooth animation
```

### パターン2: カメラズーム
```
Slow zoom in to face, cinematic, smooth camera movement
```

### パターン3: きらきらエフェクト
```
Magical sparkles floating around,
character blinks, dreamy atmosphere
```

### パターン4: 周回
```
Camera orbits around character 360°,
smooth rotation, cinematic
```

---

## 🔥 実践例：シーン別完全版プロンプト

### シーン1: アイドル風キラキラPV
**Nano Banana画像**: アイドル衣装の明るい女の子、笑顔、キラキラ背景

**Klingモーションプロンプト**:
```
Character winks playfully with a bright smile,
camera slowly rotates 30 degrees around her,
magical sparkles and light particles floating and twinkling around,
hair gently flowing in the breeze,
background bokeh shimmer with rainbow colors,
dynamic lighting with lens flare effects,
upbeat cheerful atmosphere,
smooth anime-style animation, cinematic quality, vibrant colors
```

---

### シーン2: 戦士の覚醒シーン
**Nano Banana画像**: クールな戦士、真剣な表情、エネルギーエフェクト

**Klingモーションプロンプト**:
```
Character's eyes begin to glow with intense energy,
power aura expanding outward with electric particles,
hair starts floating upward in energy surge,
dramatic lighting shift from blue to red,
camera slow push-in with slight rotation for impact,
energy crackling effects intensifying,
epic battle-ready transformation,
cinematic camera shake, high-quality VFX,
powerful atmosphere
```

---

### シーン3: 幻想的な妖精の森
**Nano Banana画像**: 妖精の女の子、翼あり、魔法の森背景

**Klingモーションプロンプト**:
```
Fairy character gently floats up and down in slow rhythm,
butterfly wings flutter delicately with iridescent shimmer,
magical fireflies and glowing particles swirl around gracefully,
soft dreamy focus with bokeh background,
camera slowly orbits revealing magical forest details,
bioluminescent plants pulsing with soft light,
ethereal mist flowing through the scene,
enchanting peaceful atmosphere,
Studio Ghibli-inspired smooth animation, 8k quality
```

---

### シーン4: コミカルな驚きリアクション（提供画像風）
**Nano Banana画像**: 大口を開けた驚き顔、誇張表現、3DCG

**Klingモーションプロンプト**:
```
Character's eyes bulge out even more in cartoonish shock,
mouth opens wider with exaggerated jaw drop,
quick head shake with rubber-band bounce effect,
comic impact lines and speed lines appearing around face,
camera slight zoom in with wobble for comedic effect,
vibrant color flash for emphasis,
over-the-top anime reaction with sound-effect-like visual timing,
high-energy cartoon physics, comedic timing,
smooth 3D animation with stylized squash and stretch
```

---

### シーン5: ロマンチックな夕暮れ
**Nano Banana画像**: 優しい表情の少女、夕日背景

**Klingモーションプロンプト**:
```
Character slowly turns head towards camera with gentle smile appearing,
soft blink with eyes reflecting golden sunset,
hair flowing gracefully in warm evening breeze,
sakura petals or light particles drifting across the scene,
camera slow pan revealing beautiful sky,
golden hour lighting gradually intensifying,
warm orange and pink tones enhancing,
romantic peaceful atmosphere,
cinematic depth of field with background softly blurred,
emotional and serene, photorealistic anime quality
```

---

## 💡 組み合わせのコツ

### 良い組み合わせ ✅
- **カメラワーク + キャラクター動き**: 「ズームイン」+「笑顔になる」
- **環境エフェクト + 表情**: 「きらきら」+「ウインク」
- **光の変化 + ドラマチックな動き**: 「ライティングシフト」+「覚醒」

### 避けるべき組み合わせ ❌
- 複数の激しいカメラワークの同時指定（混乱する）
- 静的な画像に過度に複雑な動きの要求
- 相反する雰囲気（コミカル + シリアス）

---

## 🎯 効果的なモーションプロンプトのチェックリスト

- [ ] キャラクターの動きを指定している
- [ ] カメラワークを指定している（オプション）
- [ ] 環境/エフェクトの動きを指定している（オプション）
- [ ] 雰囲気・スタイルを指定している
- [ ] プロンプトは明確で具体的
- [ ] 100単語以内に収まっている
- [ ] 動画尺（5-30秒）に適した動き量

---

## 🚀 実験的テクニック

### ループ動画向け
```
Seamless loop animation, character gentle idle motion,
continuous subtle movements,
perfect for loop, cyclic animation
```

### スローモーション強調
```
Slow-motion cinematic effect,
every detail captured beautifully,
dramatic timing, epic slow-mo
```

### タイムラプス風
```
Time-lapse style with lighting changing through day to night,
character in gentle motion, environmental transformation
```

---

## 📊 生成ログテンプレート

`outputs/production-log.md` に記録する用

```
### [日付] - [プロジェクト名]

**画像プロンプト**: [Nano Bananaで使用したプロンプト]
**モーションプロンプト**: [Klingで使用したプロンプト]
**設定**: [解像度/尺/その他設定]
**結果**: [成功/要改善]
**メモ**: [気づいた点、次回への改善点]
**ファイル**: `outputs/2026-03-16_project-name.mp4`
```

---

次のステップ: `quick-reference.md` でチートシート確認！
