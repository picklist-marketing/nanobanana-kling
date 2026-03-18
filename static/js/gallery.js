/**
 * ギャラリーページのJavaScript
 */

// ページロード時
document.addEventListener('DOMContentLoaded', function() {
    loadGallery();

    // イベントリスナー
    document.getElementById('btn-refresh-gallery').addEventListener('click', loadGallery);
    document.getElementById('btn-clear-all').addEventListener('click', clearAll);

    // モーダルを閉じる
    document.querySelector('.modal-close').addEventListener('click', closeModal);
    document.getElementById('modal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
});

/**
 * ギャラリーを読み込み
 */
function loadGallery() {
    const history = JSON.parse(localStorage.getItem('prompt-history') || '[]');
    const galleryGrid = document.getElementById('gallery-grid');
    const emptyState = document.getElementById('empty-state');

    // 生成された画像・動画のみをフィルタリング
    const generatedItems = history.filter(item =>
        item.generatedImage || item.generatedVideo
    );

    if (generatedItems.length === 0) {
        galleryGrid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    galleryGrid.style.display = 'grid';
    emptyState.style.display = 'none';
    galleryGrid.innerHTML = '';

    // 新しい順に表示（reverseしない - すでに新しい順）
    generatedItems.forEach((item, index) => {
        const card = createGalleryCard(item, index);
        galleryGrid.appendChild(card);
    });
}

/**
 * ギャラリーカードを作成
 */
function createGalleryCard(item, index) {
    const card = document.createElement('div');
    card.className = 'gallery-item';

    // 動画があれば動画を優先、なければ画像
    const hasVideo = item.generatedVideo;
    const hasImage = item.generatedImage;
    const mediaUrl = hasVideo ? item.generatedVideo : item.generatedImage;
    const mediaType = hasVideo ? 'video' : 'image';

    let mediaHtml = '';
    if (mediaType === 'video') {
        mediaHtml = `<video class="gallery-item-media" src="${mediaUrl}" muted loop onmouseover="this.play()" onmouseout="this.pause()"></video>`;
    } else {
        mediaHtml = `<img class="gallery-item-media" src="${mediaUrl}" alt="Generated">`;
    }

    // タイトル（商材カテゴリ + キャラクター）
    const title = `${item.product_category || '未設定'} × ${item.character_subject || '未設定'}`;

    // 日時
    const timestamp = item.timestamp ? new Date(item.timestamp).toLocaleString('ja-JP') : '不明';

    card.innerHTML = `
        ${mediaHtml}
        <div class="gallery-item-info">
            <div class="gallery-item-title">${title}</div>
            <div class="gallery-item-meta">
                <span class="gallery-item-type ${mediaType}">${mediaType === 'video' ? '🎬 動画' : '🎨 画像'}</span>
                <span>${timestamp}</span>
            </div>
            <div class="gallery-item-actions">
                <button class="btn btn-small btn-primary" onclick="viewItem(${index})">👁️ 詳細</button>
                <button class="btn btn-small btn-secondary" onclick="downloadItem('${mediaUrl}', '${mediaType}', ${index})">💾 保存</button>
            </div>
        </div>
    `;

    card.addEventListener('click', function(e) {
        // ボタンクリック時は除外
        if (!e.target.closest('button')) {
            viewItem(index);
        }
    });

    return card;
}

/**
 * アイテムの詳細を表示
 */
function viewItem(index) {
    const history = JSON.parse(localStorage.getItem('prompt-history') || '[]');
    const generatedItems = history.filter(item =>
        item.generatedImage || item.generatedVideo
    );

    const item = generatedItems[index];
    if (!item) return;

    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');

    const hasVideo = item.generatedVideo;
    const mediaUrl = hasVideo ? item.generatedVideo : item.generatedImage;
    const mediaType = hasVideo ? 'video' : 'image';

    let mediaHtml = '';
    if (mediaType === 'video') {
        mediaHtml = `<video class="modal-media" src="${mediaUrl}" controls autoplay loop></video>`;
    } else {
        mediaHtml = `<img class="modal-media" src="${mediaUrl}" alt="Generated">`;
    }

    modalBody.innerHTML = `
        ${mediaHtml}
        <div class="modal-info">
            <h3>📝 設定内容</h3>
            <p><strong>商材カテゴリ:</strong> ${item.product_category || '未設定'}</p>
            <p><strong>キャラクター:</strong> ${item.character_subject || '未設定'}</p>
            ${item.dialogue ? `<p><strong>セリフ:</strong> ${item.dialogue}</p>` : ''}
            ${item.character_emotion ? `<p><strong>感情:</strong> ${item.character_emotion}</p>` : ''}
            ${item.visual_style ? `<p><strong>スタイル:</strong> ${item.visual_style}</p>` : ''}
            <p><strong>生成日時:</strong> ${item.timestamp ? new Date(item.timestamp).toLocaleString('ja-JP') : '不明'}</p>
        </div>
    `;

    modal.classList.add('show');
}

/**
 * モーダルを閉じる
 */
function closeModal() {
    document.getElementById('modal').classList.remove('show');
}

/**
 * アイテムをダウンロード
 */
function downloadItem(url, type, index) {
    const link = document.createElement('a');
    link.href = url;
    link.download = `anime_cr_${type}_${Date.now()}.${type === 'video' ? 'mp4' : 'png'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * すべてクリア
 */
function clearAll() {
    if (confirm('本当にすべての履歴とギャラリーを削除しますか？')) {
        localStorage.removeItem('prompt-history');
        loadGallery();
        alert('すべての履歴が削除されました');
    }
}
