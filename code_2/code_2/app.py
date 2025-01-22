import serial
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import time

# Flask アプリケーションの初期化
app = Flask(__name__)
CORS(app)

# NMEAフォーマットの位置情報を解析する関数
def parse_nmea_lat_lon(lat, lat_dir, lon, lon_dir):
    try:
        # 緯度の計算
        raw_lat = float(lat)
        lat_deg = int(raw_lat / 100)  # 度部分
        lat_min = raw_lat - (lat_deg * 100)  # 分部分
        latitude = lat_deg + (lat_min / 60)  # 度に変換

        # 南緯なら符号を反転
        if lat_dir == 'S':
            latitude = -latitude

        # 経度の計算
        raw_lon = float(lon)
        lon_deg = int(raw_lon / 100)  # 度部分
        lon_min = raw_lon - (lon_deg * 100)  # 分部分
        longitude = lon_deg + (lon_min / 60)  # 度に変換

        # 西経なら符号を反転
        if lon_dir == 'W':
            longitude = -longitude

        return latitude, longitude
    except (ValueError, IndexError) as e:
        print(f"位置情報の解析エラー: {e}")
        return None, None

# ZED-F9PからのGNSSデータの受信と補正処理
def get_gnss_data_from_device():
    port = "COM3"  # GNSSデバイスのポート
    baud_rate = 115200  # ZED-F9Pのボーレート

    try:
        with serial.Serial(port, baud_rate, timeout=3) as ser:
            print("ZED-F9PとNEO-D9Cに接続中...")

            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                print(f"受信データ: {line}")

                # GNGGAメッセージを処理
                if line.startswith("$GNGGA"):
                    data = line.split(",")
                    if len(data) > 9:
                        latitude, longitude = parse_nmea_lat_lon(
                            data[2], data[3], data[4], data[5]
                        )
                        return {"latitude": latitude, "longitude": longitude, "clas_bytes": len(line)}

                # GNRMCメッセージを処理
                elif line.startswith("$GNRMC"):
                    data = line.split(",")
                    if len(data) > 9:
                        latitude, longitude = parse_nmea_lat_lon(
                            data[3], data[4], data[5], data[6]
                        )
                        return {"latitude": latitude, "longitude": longitude, "clas_bytes": len(line)}

                time.sleep(0.1)  # 少し待機して次のデータを受信

    except Exception as e:
        print(f"エラー: {e}")

    return {"latitude": None, "longitude": None, "clas_bytes": 0}

# GNSSデータを提供するAPIエンドポイント
@app.route('/api/gnss_data', methods=['GET'])
def get_gnss_data():
    data = get_gnss_data_from_device()  # ZED-F9P から補正データを取得
    return jsonify(data)

# フロントエンド用HTMLを提供
@app.route('/')
def index():
    return render_template('index.html')

# メイン処理
if __name__ == '__main__':
    app.run(debug=True)
