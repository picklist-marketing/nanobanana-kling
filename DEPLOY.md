# Vercelデプロイ手順

## 準備

1. Vercelアカウントを作成（まだの場合）
   https://vercel.com/signup

2. Vercel CLIをインストール（オプション）
   ```bash
   npm install -g vercel
   ```

## デプロイ方法

### 方法1: GitHub連携（推奨）

1. GitHubにリポジトリをプッシュ
   ```bash
   cd /Users/muraseatsuki/Projects/nanobanana-kling
   git init
   git add .
   git commit -m "Initial commit for Vercel deployment"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. Vercelダッシュボードで「New Project」をクリック
3. GitHubリポジトリをインポート
4. プロジェクト設定はデフォルトのままでOK
5. 「Deploy」をクリック

### 方法2: Vercel CLI

1. プロジェクトディレクトリに移動
   ```bash
   cd /Users/muraseatsuki/Projects/nanobanana-kling
   ```

2. Vercelにログイン
   ```bash
   vercel login
   ```

3. デプロイ
   ```bash
   vercel
   ```

4. 本番デプロイ
   ```bash
   vercel --prod
   ```

## 注意事項

- 履歴機能はブラウザのlocalStorageに保存されます（サーバー側には保存されません）
- ブラウザのキャッシュをクリアすると履歴も消えます
- 各ブラウザ/デバイスごとに独立した履歴が保存されます

## 環境変数

特に必要な環境変数はありません。

## トラブルシューティング

### ビルドエラーが出る場合
- requirements.txtが正しいか確認
- Python 3.9以上が使われているか確認

### 静的ファイルが読み込まれない場合
- vercel.jsonのroutesが正しいか確認

## カスタムドメイン設定

1. Vercelダッシュボードでプロジェクトを開く
2. Settings > Domains に移動
3. カスタムドメインを追加
