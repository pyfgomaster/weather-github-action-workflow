import requests
import csv
import json

def fetch_cwa_data(api_key, data_id):
    """
    從中央氣象署開放資料平台抓取 JSON 格式的資料。
    """
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{data_id}?Authorization={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查 HTTP 狀態碼
        response.encoding = 'utf-8'  # 確保回應的編碼正確
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 抓取資料失敗：{e}")
        return None

def save_selected_weather_data_to_csv(data, filename="api.csv"):
    """
    將天氣資料 JSON 轉換為 CSV 格式，並提取指定的欄位。
    """
    if not data or not data.get('records') or not data['records'].get('location'):
        print("⚠️ 沒有資料可以處理")
        return

    locations = data['records']['location']

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["地點", "開始時間", "結束時間", "降雨機率", "最小溫度", "最大溫度"])  # 寫入標題

        for location in locations:
            location_name = location['locationName']
            pop_times = []
            min_temp_times = []
            max_temp_times = []

            for element in location['weatherElement']:
                if element['elementName'] == 'PoP':
                    pop_times = element['time']
                elif element['elementName'] == 'MinT':
                    min_temp_times = element['time']
                elif element['elementName'] == 'MaxT':
                    max_temp_times = element['time']

            # 提取需要的資料並寫入 CSV
            for pop_time in pop_times:
                start_time = pop_time['startTime']
                end_time = pop_time['endTime']
                rain_probability = pop_time['parameter']['parameterName']

                # 找到對應時間的溫度資料
                min_temp = next((t['parameter']['parameterName'] for t in min_temp_times if t['startTime'] == start_time), '')
                max_temp = next((t['parameter']['parameterName'] for t in max_temp_times if t['startTime'] == start_time), '')

                writer.writerow([location_name, start_time, end_time, rain_probability, min_temp, max_temp])

    print(f"📄 資料已儲存到 {filename}")

if __name__ == '__main__':
    api_key = "CWA-682CAEA6-5154-4FDA-B2EF-499BDB8C9AFD"  # 你的 API 金鑰
    data_id = "F-C0032-001"

    weather_data = fetch_cwa_data(api_key, data_id)
    if weather_data:
        save_selected_weather_data_to_csv(weather_data)