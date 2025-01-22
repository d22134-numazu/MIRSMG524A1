// Leaflet.js で地図を初期化
const map = L.map('map').setView([35.0755,138.5316], 13);  // 初期位置（沼津高専）

// OpenStreetMapのタイルレイヤーを追加
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// 移動経路を描画するための配列
let route = [];  // 過去の位置情報を格納する配列
let marker;  // 現在のマーカー
let polyline;  // 移動経路を表示するための線

// サーバーからGNSSデータを取得する関数
const fetchGNSSData = async () => {
    try {
        const response = await fetch('/api/gnss_data');
        if (!response.ok) {
            throw new Error(`HTTPエラー: ${response.status}`);
        }
        const data = await response.json();

        // データが存在し、latitude と longitude が有効か確認
        if (data && data.latitude != null && data.longitude != null) {
            // 新しい位置を追加
            const newLatLng = [data.latitude, data.longitude];

            // 移動経路（線）の更新
            route.push(newLatLng);

            // 移動経路（線）を描画
            if (polyline) {
                polyline.setLatLngs(route);  // 既存の線を更新
            } else {
                polyline = L.polyline(route, { color: 'blue' }).addTo(map);  // 新しい線を追加
            }

            // 地図の中心を更新
            map.setView(newLatLng, 18);

            // 現在の位置にマーカーを表示
            if (marker) {
                marker.setLatLng(newLatLng);  // マーカーの位置を更新
            } else {
                marker = L.marker(newLatLng).addTo(map);  // 新しいマーカーを追加
            }

            // 受信したデータを表示
            document.getElementById('latitude').innerText = data.latitude.toFixed(6);
            document.getElementById('longitude').innerText = data.longitude.toFixed(6);
        } else {
            console.warn('無効なGNSSデータ:', data);
            document.getElementById('latitude').innerText = 'N/A';
            document.getElementById('longitude').innerText = 'N/A';
        }

    } catch (error) {
        console.error('データ取得中にエラーが発生しました:', error);

        // エラー時のUIリセット
        document.getElementById('latitude').innerText = 'N/A';
        document.getElementById('longitude').innerText = 'N/A';
    }
};

// 定期的にデータを取得 (5秒ごと)
setInterval(fetchGNSSData, 5000);

// 初回実行
fetchGNSSData();