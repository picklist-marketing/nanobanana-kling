# 🚀 クイックリファレンス・チートシート

制作中にサッと確認できる簡潔版ガイド

---

## ⚡ 30秒で始める最速フロー

1. **Nano Banana**: 下記のテンプレートコピー → `[  ]`埋める → 生成
2. **保存**: 画像を `outputs/` に保存（ファイル名: `2026-03-16_描写_001.png`）
3. **Kling**: 画像アップロード → モーションプロンプト貼り付け → 生成

---

## 📝 超シンプルテンプレート（Nano Banana用）

### 基本フォーマット
```
[キャラ], [髪], [目], [表情], [服],
[スタイル], [アングル], [光], [背景], 8k octane render
```

### 記入例
```
Cute anime girl, pink twin-tails, big blue eyes, smile, school uniform,
Pixar 3D style, close-up, soft light, gradient background, 8k octane render
```

---

## 🎨 スタイル早見表（Nano Banana）

| スタイル名 | 特徴 | 用途 |
|----------|------|------|
| `Pixar style` | 丸くて可愛い | 日常/コメディ |
| `Disney 3D style` | 美しく洗練 | ファンタジー/美麗 |
| `Arcane style` | スタイリッシュ | クール/都会的 |
| `Ghibli 3D style` | 柔らかく温かい | 癒し/ファンタジー |
| `Game cinematic style` | リアル寄り | アクション/RPG |

---

## 📐 カメラアングル早見表

| アングル | 効果 |
|---------|------|
| `close-up` | 表情重視、感情表現 |
| `low angle` | 迫力、ヒロイック |
| `high angle` | 可愛さ、脆弱性 |
| `dutch angle` | 緊張感、不安定 |
| `extreme close-up` | ディテール、インパクト |

---

## 💡 ライティング早見表

| ライト | 雰囲気 |
|-------|--------|
| `soft diffused lighting` | 優しい、穏やか |
| `dramatic lighting` | 緊張感、ドラマチック |
| `volumetric lighting` | 神秘的、幻想的 |
| `rim lighting` | スタイリッシュ、クール |
| `golden hour lighting` | ロマンチック、ノスタルジック |

---

## 🎬 モーションプロンプト早見表（Kling用）

### 基本動作

| 動作 | プロンプト |
|------|----------|
| 笑顔 | `Character smiles, eyes light up, hair sways` |
| まばたき | `Natural blink, subtle breathing, gentle motion` |
| ウインク | `Playful wink, slight smile, cheerful` |
| 驚き | `Eyes widen, mouth opens, quick head movement` |

### カメラワーク

| 動き | プロンプト |
|------|----------|
| ズームイン | `Slow zoom in, focus on face, cinematic` |
| 周回 | `Camera orbits 360°, smooth rotation` |
| 上下パン | `Camera pans up, revealing character` |
| プッシュイン | `Fast push-in with rotation, dynamic` |

### エフェクト

| エフェクト | プロンプト |
|----------|----------|
| きらきら | `Magical sparkles floating, glowing, dreamy` |
| 風 | `Wind effect, hair flowing, leaves blowing` |
| 光変化 | `Lighting shifts, shadows moving, atmospheric` |

---

## 🔥 即使えるプロンプトセット

### セット1: 可愛い日常系

**Nano Banana**:
```
Cheerful anime girl, short brown hair, big hazel eyes, bright smile,
school uniform with ribbon, Pixar 3D style, medium shot,
soft natural lighting, classroom background, 8k octane render
```

**Kling**:
```
Character smiles naturally, gentle blink, hair flows softly,
magical sparkles floating around, warm atmosphere, smooth animation
```

---

### セット2: クール戦士系

**Nano Banana**:
```
Cool warrior boy, silver spiky hair, red glowing eyes, serious face,
futuristic armor, high-quality 3D anime style, low angle hero shot,
dramatic side lighting, battlefield background, 8k unreal engine
```

**Kling**:
```
Eyes glow brighter, power aura expanding, hair whips upward,
camera slow zoom with rotation, energy particles, epic atmosphere
```

---

### セット3: ファンタジー妖精

**Nano Banana**:
```
Delicate fairy girl, translucent wings, pastel rainbow hair,
gentle smile, flower petal dress, Ghibli 3D style, soft close-up,
magical volumetric lighting, enchanted forest, 8k octane render
```

**Kling**:
```
Fairy floats gently, wings flutter, magical particles swirling,
camera orbits slowly, bioluminescent glow, dreamy atmosphere
```

---

### セット4: コミカルリアクション

**Nano Banana**:
```
Chibi anime character, huge shocked eyes, wide open mouth,
exaggerated surprise, cartoon 3D style, extreme close-up,
vibrant colors, comic background with speed lines, 8k
```

**Kling**:
```
Eyes bulge more, mouth opens wider, head shake bounce,
comic impact lines appear, camera wobble, over-the-top reaction
```

---

## 🎯 品質を上げる必須タグ

### Nano Banana用
```
highly detailed, octane render, 8k, cinematic quality
```

### Kling用
```
smooth animation, cinematic, high quality, coherent movement
```

---

## ⚠️ よくある失敗と対策

| 問題 | 原因 | 対策 |
|------|------|------|
| ぼやけた画像 | 品質タグ不足 | `8k octane render` 追加 |
| 不自然な動き | プロンプト曖昧 | 具体的な動作を記述 |
| スタイル不一致 | スタイル指定なし | `Pixar style` など明記 |
| 動画が静的 | モーション指示弱い | カメラワーク追加 |

---

## 📊 ファイル命名規則

```
YYYY-MM-DD_[スタイル]_[番号].[拡張子]

例:
2026-03-16_pixar_001.png
2026-03-16_pixar_001.mp4
```

---

## 🔄 反復改善フロー

1. **生成** → Nano Banana & Kling
2. **評価** → 何が良い/悪いか記録
3. **調整** → プロンプト微修正
4. **再生成** → 改善版作成
5. **記録** → `production-log.md` に記載

---

## 💾 プロジェクト保存先

```
nanobanana-kling/
├── prompts/          ← テンプレート（このファイル）
├── outputs/          ← 生成物の保存先
│   ├── 2026-03-16_pixar_001.png
│   ├── 2026-03-16_pixar_001.mp4
│   └── production-log.md
└── references/       ← 参考画像
```

---

## 🌟 プロのワンポイント

### ✅ DO
- **具体的に書く**: "cute girl" → "cheerful teenage girl with pink twin-tails"
- **スタイル明記**: 必ず `[スタイル] style` を含める
- **動きを想像**: Kling用に少し動きのある構図
- **記録を残す**: 良かったプロンプトを `production-log.md` に

### ❌ DON'T
- **曖昧な表現**: "good", "nice", "beautiful" だけ
- **プロンプト過多**: 200単語超えると混乱
- **スタイル混在**: "Pixar + realistic + anime" など
- **静的すぎる構図**: Klingで動かしにくい

---

## 🎁 ボーナス: ワンクリックプロンプト

超シンプル版（10秒で使える）

```
Cute anime girl, Pixar 3D, smile, 8k
```

これだけでも生成可能！詳細を足すほど精度UP。

---

## 📚 詳細版への参照

- **Nano Banana詳細**: `3dcg-templates.md`
- **Kling詳細**: `motion-prompts.md`
- **プロジェクトガイド**: `../README.md`

---

**さあ、創作を始めよう！ 🚀✨**
