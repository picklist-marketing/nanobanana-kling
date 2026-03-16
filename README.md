# 🎨 Nano Banana × Kling プロンプト生成UI

Nano BananaとKlingを使ったアニメ風キャラクター動画のプロンプト生成ツール

## 🌟 機能

- **商材に合わせた柔軟なキャラクター生成**
  - 歯垢、毛根、角栓など、あらゆる部位をキャラ化
  - 部位に応じた質感・色・環境の自動推測

- **豊富な感情表現** (26種類)
  - ネガティブ/ポジティブ × 高/低テンション
  - パニック、大笑い、眠いなど多様な表情

- **Kling公式フォーマット対応**
  - 構造化プロンプト (Subject/Context/Action/Style/Camera/Composition/Effects)
  - 任意のセリフ入力 + 自動リップシンク生成

- **縦長動画対応**
  - 9:16アスペクト比（TikTok/Instagram Reels向け）

## 🚀 使い方

### ローカル環境

```bash
# 仮想環境作成 & 依存関係インストール
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# サーバー起動
python app.py
```

http://localhost:5051 でアクセス

### Vercel デプロイ

詳細は [DEPLOY.md](DEPLOY.md) を参照

## 📝 入力項目

- **商材カテゴリ**: 歯磨き粉、育毛剤、化粧水など
- **何をキャラにするか**: 歯垢、毛根、角栓、舌など
- **セリフ（任意）**: 英語のセリフ
- **感情・テンション**: 26種類から選択
- **ビジュアルスタイル**: グロテスクコメディ、可愛いPixar風など
- **カメラアングル**: 超クローズアップ、表面視点など

## 🎬 出力

- **Nano Banana用プロンプト**: 画像生成用
- **Kling用プロンプト**: 動画化用（構造化フォーマット）

## 💾 履歴機能

- ブラウザのlocalStorageに保存（最大100件）
- 保存/読込/削除機能

## 🛠️ 技術スタック

- **Backend**: Python 3.14 + Flask
- **Frontend**: Vanilla JavaScript
- **Deployment**: Vercel対応

## 📄 ライセンス

MIT
