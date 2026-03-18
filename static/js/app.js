// グローバル状態
let currentFormData = null;
let currentPrompts = null;

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    setupEventListeners();
});

// イベントリスナー設定
function setupEventListeners() {
    // フォーム送信
    document.getElementById('prompt-form').addEventListener('submit', handleFormSubmit);

    // 履歴更新ボタン
    document.getElementById('btn-refresh-history').onclick = loadHistory;
}

// フォーム送信処理
async function handleFormSubmit(e) {
    e.preventDefault();

    // フォームデータ取得
    const formData = new FormData(e.target);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }

    currentFormData = data;

    // ローディング表示
    showToast('🔄 プロンプトを生成中...', 'info');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('生成に失敗しました');
        }

        const result = await response.json();
        currentPrompts = result;

        // プロンプトを表示
        document.getElementById('prompt-nano').value = result.nano_banana;
        document.getElementById('prompt-kling').value = result.kling;

        // サマリーを表示
        updateSummary(data);

        // ボタンを有効化
        enableButtons();

        // 自動保存
        await saveToHistory();

        showToast('✅ プロンプトを生成しました！');
    } catch (error) {
        showToast('❌ 生成に失敗しました: ' + error.message, 'error');
    }
}

// サマリーを更新
function updateSummary(data) {
    const summary = document.getElementById('summary');
    let html = `
        <div style="margin-bottom: 12px;"><strong>商材:</strong> ${data.product_category}</div>
        <div style="margin-bottom: 12px;"><strong>キャラクター:</strong> ${data.character_subject}</div>
    `;

    if (data.dialogue && data.dialogue.trim()) {
        html += `<div style="margin-bottom: 12px;"><strong>セリフ:</strong> "${data.dialogue}"</div>`;
    }

    if (data.additional_direction && data.additional_direction.trim()) {
        html += `<div style="margin-bottom: 12px;"><strong>補足演出:</strong> ${data.additional_direction}</div>`;
    }

    html += `
        <div style="margin-bottom: 12px;"><strong>感情:</strong> ${getEmotionLabel(data.character_emotion)}</div>
        <div><strong>スタイル:</strong> ${getStyleLabel(data.visual_style)}</div>
    `;

    summary.innerHTML = html;
}

// 感情ラベル取得
function getEmotionLabel(value) {
    const map = {
        // ネガティブ（高テンション）
        'panicked and terrified': 'パニック・恐怖',
        'desperate and pleading': '必死・懇願',
        'angrily shouting': '怒って叫ぶ',
        'screaming in horror': '絶叫・ホラー',
        'crying and sobbing loudly': '大泣き・号泣',
        'shocked and stunned': 'ショック・呆然',
        // ネガティブ（低テンション）
        'suffering in pain': '苦しみ・痛み',
        'exhausted and tired': '疲労・ダルい',
        'depressed and gloomy': '落ち込み・憂鬱',
        'disgusted and repulsed': '嫌悪・うんざり',
        'scared and trembling': '怯え・震え',
        'sleepy and drowsy': '眠い・うとうと',
        // ポジティブ（高テンション）
        'excited and hyper': '興奮・ハイテンション',
        'laughing hysterically': '大笑い・爆笑',
        'amazed and impressed': '驚き・感動',
        'happy and grateful': '喜び・感謝',
        'cheerful and energetic': '元気・明るい',
        // ポジティブ（低テンション）
        'relieved and comfortable': '安堵・快適',
        'satisfied and content': '満足・満たされた',
        'peaceful and calm': '穏やか・落ち着き',
        'smug and confident': '得意げ・自信満々',
        // その他
        'confused and puzzled': '困惑・戸惑い',
        'angry and frustrated': '怒り・イライラ',
        'curious and intrigued': '興味津々・好奇心',
        'mischievous and playful': 'いたずら・遊び心',
    };
    return map[value] || value;
}

// スタイルラベル取得
function getStyleLabel(value) {
    const map = {
        'grotesque comedy, Pixar meets body horror': 'グロテスクコメディ',
        'cute and friendly Pixar animation': '可愛いPixar風',
        'medical educational illustration': '医学教育風',
        'dark horror aesthetic': 'ホラー風',
        'vibrant cartoon style': '明るいカートゥーン',
    };
    return map[value] || value;
}

// ボタンを有効化
function enableButtons() {
    document.querySelectorAll('#btn-copy-nano, #btn-copy-kling').forEach(btn => {
        btn.disabled = false;
    });
    // 自動生成ボタンを有効化
    document.getElementById('btn-generate-image').disabled = false;
    document.getElementById('btn-auto-generate').disabled = false;
    // 動画生成ボタンは画像生成後に有効化
}

// プロンプトをコピー
async function copyPrompt(type) {
    let text = '';

    if (type === 'nano') {
        text = document.getElementById('prompt-nano').value;
    } else if (type === 'kling') {
        text = document.getElementById('prompt-kling').value;
    } else if (type === 'both') {
        const nano = document.getElementById('prompt-nano').value;
        const kling = document.getElementById('prompt-kling').value;
        text = `📸 Nano Banana:\n${nano}\n\n🎬 Kling:\n${kling}`;
    }

    try {
        await navigator.clipboard.writeText(text);
        showToast('📋 クリップボードにコピーしました！');
    } catch (error) {
        showToast('コピーに失敗しました', 'error');
    }
}

// Nano Bananaにコピー&開く
async function copyAndOpenNanoBanana() {
    const text = document.getElementById('prompt-nano').value;
    if (!text) {
        showToast('プロンプトを生成してください', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showToast('📋 Nano Banana用プロンプトをコピーしました！Geminiを開きます...');
        // Gemini (Nano Banana)のサイトを開く
        window.open('https://gemini.google.com/app', '_blank');
    } catch (error) {
        showToast('コピーに失敗しました', 'error');
    }
}

// Klingにコピー&開く
async function copyAndOpenKling() {
    const text = document.getElementById('prompt-kling').value;
    if (!text) {
        showToast('プロンプトを生成してください', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showToast('📋 Kling用プロンプトをコピーしました！Higgsfieldを開きます...');
        // Higgsfield (Kling)のサイトを開く
        window.open('https://higgsfield.ai/create/video', '_blank');
    } catch (error) {
        showToast('コピーに失敗しました', 'error');
    }
}

// 履歴に保存（自動保存）
async function saveToHistory() {
    if (!currentFormData || !currentPrompts) {
        return;
    }

    const data = {
        ...currentFormData,
        nano_banana: document.getElementById('prompt-nano').value,
        kling: document.getElementById('prompt-kling').value,
    };

    try {
        // localStorageに保存
        const localHistory = localStorage.getItem('prompt-history');
        let history = localHistory ? JSON.parse(localHistory) : [];

        // タイムスタンプとIDを追加
        data.timestamp = new Date().toISOString();
        data.id = Date.now();

        // 先頭に追加して最新100件のみ保持
        history.unshift(data);
        history = history.slice(0, 100);

        localStorage.setItem('prompt-history', JSON.stringify(history));

        // 履歴を更新（トースト通知なし）
        loadHistory();
    } catch (error) {
        console.error('Failed to save history:', error);
    }
}

// 生成されたメディアを履歴に追加
function updateHistoryWithGeneratedMedia(type, url) {
    try {
        const localHistory = localStorage.getItem('prompt-history');
        if (!localHistory) return;

        let history = JSON.parse(localHistory);
        if (history.length === 0) return;

        // 最新のエントリーに追加
        const latestEntry = history[0];
        if (type === 'image') {
            latestEntry.generatedImage = url;
        } else if (type === 'video') {
            latestEntry.generatedVideo = url;
        }

        localStorage.setItem('prompt-history', JSON.stringify(history));
    } catch (error) {
        console.error('Failed to update history with generated media:', error);
    }
}

// 履歴を読み込み
async function loadHistory() {
    try {
        // まずlocalStorageから読み込み
        const localHistory = localStorage.getItem('prompt-history');
        if (localHistory) {
            const history = JSON.parse(localHistory);
            renderHistory(history);
            return;
        }

        // localStorageになければAPIから読み込み（ローカル環境用）
        const response = await fetch('/api/history');
        const history = await response.json();
        renderHistory(history);
    } catch (error) {
        showToast('履歴の読み込みに失敗しました', 'error');
    }
}

// 履歴を描画
function renderHistory(history) {
    const container = document.getElementById('history-list');
    container.innerHTML = '';

    if (history.length === 0) {
        container.innerHTML = '<p style="color: #868e96; text-align: center; padding: 20px; font-size: 0.9rem;">履歴がありません</p>';
        return;
    }

    history.forEach(item => {
        const itemEl = document.createElement('div');
        itemEl.className = 'history-item';

        const headerEl = document.createElement('div');
        headerEl.className = 'history-item-header';

        const titleEl = document.createElement('div');
        titleEl.className = 'history-item-title';
        titleEl.textContent = item.product_category;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'history-item-delete';
        deleteBtn.textContent = '🗑️';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteHistoryItem(item.id);
        };

        headerEl.appendChild(titleEl);
        headerEl.appendChild(deleteBtn);

        const categoryEl = document.createElement('div');
        categoryEl.className = 'history-item-category';
        const dialogueText = item.dialogue ? ` - "${item.dialogue.substring(0, 20)}..."` : '';
        categoryEl.textContent = `${item.character_subject}${dialogueText}`;

        const timeEl = document.createElement('div');
        timeEl.className = 'history-item-time';
        timeEl.textContent = formatTime(item.timestamp);

        itemEl.appendChild(headerEl);
        itemEl.appendChild(categoryEl);
        itemEl.appendChild(timeEl);

        itemEl.onclick = () => loadFromHistory(item);

        container.appendChild(itemEl);
    });
}

// 履歴から読み込み
function loadFromHistory(item) {
    // フォームに値を設定
    document.getElementById('product_category').value = item.product_category || '';
    document.getElementById('character_subject').value = item.character_subject || '';
    document.getElementById('dialogue').value = item.dialogue || '';
    document.getElementById('additional_direction').value = item.additional_direction || '';
    document.getElementById('character_emotion').value = item.character_emotion || 'panicked and terrified';
    document.getElementById('visual_style').value = item.visual_style || 'grotesque comedy, Pixar meets body horror';
    document.getElementById('camera_angle').value = item.camera_angle || 'extreme close-up POV from inside';

    // プロンプトを表示
    document.getElementById('prompt-nano').value = item.nano_banana || '';
    document.getElementById('prompt-kling').value = item.kling || '';

    // サマリーを更新
    updateSummary(item);

    // ボタンを有効化
    enableButtons();

    // 現在のデータを保存
    currentFormData = item;
    currentPrompts = {
        nano_banana: item.nano_banana,
        kling: item.kling
    };

    showToast('📖 履歴から読み込みました');

    // フォームまでスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 履歴を削除
async function deleteHistoryItem(id) {
    if (!confirm('この履歴を削除しますか？')) {
        return;
    }

    try {
        // localStorageから削除
        const localHistory = localStorage.getItem('prompt-history');
        if (localHistory) {
            let history = JSON.parse(localHistory);
            history = history.filter(h => h.id !== id);
            localStorage.setItem('prompt-history', JSON.stringify(history));
        }

        showToast('🗑️ 削除しました');
        loadHistory();
    } catch (error) {
        showToast('削除に失敗しました', 'error');
    }
}

// 時刻をフォーマット
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
        return 'たった今';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分前`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}時間前`;
    } else {
        return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }
}

// トースト通知を表示
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ==============================
// 自動生成機能（Google AI統合）
// ==============================

let generatedImageFilename = null;

// 画像生成
async function generateImage() {
    if (!currentPrompts || !currentPrompts.nano_banana) {
        showToast('⚠️ まずプロンプトを生成してください', 'error');
        return;
    }

    const btn = document.getElementById('btn-generate-image');
    btn.disabled = true;
    btn.innerHTML = '🔄 画像生成中...';

    showToast('🎨 Imagen 3で画像を生成中...', 'info');

    try {
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: currentPrompts.nano_banana
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '画像生成に失敗しました');
        }

        const result = await response.json();

        if (result.success) {
            // 画像を表示
            document.getElementById('generated-image').src = result.image_url;
            document.getElementById('image-result').style.display = 'block';
            generatedImageFilename = result.image_filename;

            // 動画生成ボタンを有効化
            document.getElementById('btn-generate-video').disabled = false;

            // localStorageに画像URLを保存
            updateHistoryWithGeneratedMedia('image', result.image_url);

            showToast('✅ 画像生成完了！');
        } else {
            throw new Error(result.error || '画像生成に失敗しました');
        }
    } catch (error) {
        showToast('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🎨 画像生成';
    }
}

// 動画生成
async function generateVideo() {
    if (!currentPrompts || !currentPrompts.kling) {
        showToast('⚠️ まずプロンプトを生成してください', 'error');
        return;
    }

    const btn = document.getElementById('btn-generate-video');
    btn.disabled = true;
    btn.innerHTML = '🔄 動画生成中...（数分かかります）';

    showToast('🎬 Veo 3.1で動画を生成中...お待ちください', 'info');

    try {
        const response = await fetch('/api/generate-video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: currentPrompts.kling,
                image_filename: generatedImageFilename,
                dialogue: currentFormData?.dialogue || ''
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '動画生成に失敗しました');
        }

        const result = await response.json();

        if (result.success) {
            // 動画を表示
            const video = document.getElementById('generated-video');
            video.src = result.video_url;
            document.getElementById('video-result').style.display = 'block';

            // localStorageに動画URLを保存
            updateHistoryWithGeneratedMedia('video', result.video_url);

            showToast('✅ 動画生成完了！');
        } else {
            throw new Error(result.error || '動画生成に失敗しました');
        }
    } catch (error) {
        showToast('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🎬 動画生成';
    }
}

// 一括自動生成（画像→動画）
async function autoGenerateFull() {
    if (!currentPrompts) {
        showToast('⚠️ まずプロンプトを生成してください', 'error');
        return;
    }

    const btn = document.getElementById('btn-auto-generate');
    const status = document.getElementById('auto-generate-status');

    btn.disabled = true;
    btn.innerHTML = '🔄 自動生成中...';

    try {
        // ステップ1: 画像生成
        status.innerHTML = '<p style="color: #2196F3;">🎨 ステップ1/2: Imagen 3で画像生成中...</p>';
        showToast('🎨 画像生成中...', 'info');

        const imageResponse = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: currentPrompts.nano_banana
            })
        });

        if (!imageResponse.ok) {
            const error = await imageResponse.json();
            throw new Error(error.error || '画像生成に失敗しました');
        }

        const imageResult = await imageResponse.json();

        if (!imageResult.success) {
            throw new Error(imageResult.error || '画像生成に失敗しました');
        }

        // 画像を表示
        document.getElementById('generated-image').src = imageResult.image_url;
        document.getElementById('image-result').style.display = 'block';

        // localStorageに画像URLを保存
        updateHistoryWithGeneratedMedia('image', imageResult.image_url);

        status.innerHTML += '<p style="color: #4CAF50;">✅ 画像生成完了！</p>';

        // ステップ2: 動画生成
        status.innerHTML += '<p style="color: #2196F3;">🎬 ステップ2/2: Veo 3.1で動画生成中...（数分かかります）</p>';
        showToast('🎬 動画生成中...お待ちください', 'info');

        const videoResponse = await fetch('/api/generate-video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: currentPrompts.kling,
                image_filename: imageResult.image_filename,
                dialogue: currentFormData?.dialogue || ''
            })
        });

        if (!videoResponse.ok) {
            const error = await videoResponse.json();
            throw new Error(error.error || '動画生成に失敗しました');
        }

        const videoResult = await videoResponse.json();

        if (!videoResult.success) {
            throw new Error(videoResult.error || '動画生成に失敗しました');
        }

        // 動画を表示
        const video = document.getElementById('generated-video');
        video.src = videoResult.video_url;
        document.getElementById('video-result').style.display = 'block';

        // localStorageに動画URLを保存
        updateHistoryWithGeneratedMedia('video', videoResult.video_url);

        status.innerHTML += '<p style="color: #4CAF50;">✅ 動画生成完了！</p>';
        status.innerHTML += '<p style="color: #4CAF50; font-weight: bold;">🎉 すべての生成が完了しました！</p>';

        showToast('🎉 画像・動画の生成が完了しました！');

    } catch (error) {
        status.innerHTML += `<p style="color: #f44336;">❌ エラー: ${error.message}</p>`;
        showToast('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 一括自動生成（Imagen 3 → Veo 3.1）';
    }
}
