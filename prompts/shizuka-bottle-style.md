# しずかボトルスタイル プロンプトテンプレート

## 🎯 用途
「しずか」天然水のTikTok広告CR。商品ボトルを擬人化して海底で語らせるスタイル。
セリフは毎回変わるため、キャラ設定と演出のみ定義。

---

## 🧊 商品スペック

- 透明クリアボトル / 白キャップ
- ラベルに大きな青い水滴ロゴ
- 「自然が育てた日本の水 500ml」
- ナトリウム 7.99mg / マグネシウム 0.95mg

---

## 🎭 キャラ生成（静止画）

商品画像（商品画像 5018.jpg）を参考画像として添付し、以下で生成。
一度生成したキャラ画像を保存して、以降のImage to Videoで使い回す。

### Nano Banana / SORA
```
A cute Pixar-style 3D anthropomorphic version of this exact water bottle.
Keep the exact same bottle design — clear transparent body, white cap,
blue water droplet logo, label text.
Add large expressive cartoon eyes on upper body,
a small animated mouth below the label,
small white-gloved hands on the sides.
Standing on colorful coral reef underwater,
tropical fish, bubbles, soft blue-green god ray lighting.
Highly detailed, octane render, 8k, vertical 9:16.
```

### 表情バリエーション（キャラ画像を複数作っておく）

| 表情 | 追加プロンプト |
|------|-------------|
| 笑顔（デフォルト） | `warm friendly smile, eyes slightly squinted with joy` |
| 驚き | `eyes wide open, mouth in O shape, both hands on cheeks` |
| 自信 | `confident smirk, one hand on hip, slight head tilt` |
| 説教 | `stern serious expression, one finger raised, furrowed brows` |
| 興奮 | `huge excited grin, sparkling eyes, both fists raised` |
| ウインク | `one eye winking, playful smile, pointing at camera` |

---

## 🎬 演出テンプレート（動画 / Kling Image to Video）

上で生成したキャラ静止画をKling Image to Videoに入れて使う。

### ベース演出（毎回共通）
```
The water bottle character stands on coral reef underwater,
talking directly to camera with natural mouth movement and hand gestures.
Eyes blink naturally.
Water inside the transparent body subtly sloshes with each movement.
Bubbles rise continuously around the character.
Small tropical fish occasionally swim past.
Coral sways gently with underwater current.
Soft caustic light patterns dance across the scene.
Smooth Pixar-quality 3D animation, vertical 9:16.
```

### 演出バリエーション（ベースに追加）

| 演出 | 追加プロンプト |
|------|-------------|
| 語りかけ | `Character talks calmly with warm smile, one hand raised, gentle swaying` |
| 驚かせる | `Eyes go wide, leans back dramatically, then leans forward pointing at camera` |
| 自信ある説明 | `Nods confidently, one hand on hip, other hand counting on fingers` |
| お得アピール | `Jumps excitedly, arms spread wide, bouncing with enthusiasm` |
| CTA | `Leans close to camera, winks, points at viewer, warm inviting gesture` |

---

## 📐 制作フロー

```
1. 商品画像をアップ → キャラ静止画を生成（表情別に数パターン）
2. セリフ台本を用意
3. セリフに合う表情のキャラ画像を選ぶ
4. Kling Image to Video にキャラ画像 + ベース演出 + 演出バリエーション
5. 生成された動画にテロップ（セリフ）を後乗せ
6. AIボイスで音声を後付け
7. 縦型9:16で書き出し
```

---

## 🌊 背景バリエーション（海底以外も可）

| 背景 | プロンプト |
|------|-----------|
| 海底サンゴ礁（デフォルト） | `underwater coral reef, tropical fish, bubbles, blue-green god ray lighting` |
| 清流・湧き水 | `crystal clear mountain spring, smooth rocks, lush green moss, sunlight filtering through trees` |
| 氷の洞窟 | `inside a beautiful ice cave, transparent blue ice walls, frost particles, cold blue lighting` |
| 朝のキッチン | `bright modern kitchen, morning sunlight through window, clean white counter, fresh atmosphere` |
