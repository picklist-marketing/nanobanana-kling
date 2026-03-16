#!/bin/bash

# Nano Banana × Kling プロンプト管理UI 起動スクリプト

cd "$(dirname "$0")"

echo "=========================================="
echo "🎨 Nano Banana × Kling プロンプト管理UI"
echo "=========================================="
echo ""

# Python仮想環境チェック
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成中..."
    python3 -m venv venv
    echo "✅ 仮想環境を作成しました"
fi

# 仮想環境を有効化
echo "🔧 仮想環境を有効化中..."
source venv/bin/activate

# 依存関係をインストール
echo "📥 依存関係をインストール中..."
pip install -q -r requirements.txt

echo ""
echo "✅ 準備完了！サーバーを起動します..."
echo ""

# Flaskアプリを起動
python app.py
