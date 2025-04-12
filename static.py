import requests
import csv
import time

def fetch_data(url, headers, params):
    """抓取網頁資料"""
    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()  # 檢查 HTTP 狀態碼
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求錯誤：{e}")
        return None

def parse_data(data):
    """解析 JSON 資料，提取需要的職缺資訊"""
    jobs = []
    try:
        if data and data['data'] and data['data']['list']:  # 確保資料存在
            for job in data['data']['list']:
                job_name = job.get('jobName', '')
                company = job.get('custName', '')
                address = job.get('jobAddrNoDesc', '')
                link = f"https://www.104.com.tw/job/{job.get('jobNo', '')}"  # 使用 .get()
                
                jobs.append([job_name, company, address, link])
        else:
            print("⚠️  沒有找到職缺資料")
    except KeyError as e:
        print(f"❌  JSON 格式錯誤：{e}")
    return jobs

def save_to_csv(filename, data):
    """將職缺資訊寫入 CSV 檔案"""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["職缺名稱", "公司名稱", "地區", "網址"])
        writer.writerows(data)
    print(f"📄 已成功寫入 {filename}")

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.104.com.tw/jobs/search/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"
    }

    url = "https://www.104.com.tw/jobs/search/list"
    params = {
        "ro": "0",
        "kwop": "1",
        "keyword": "Python",
        "order": "11",
        "page": "1",
        "mode": "s",
        "jobsource": "2018indexpoc"
    }

    all_jobs = []
    page = 1
    while True:  # 迴圈抓取多頁資料
        params['page'] = page
        data = fetch_data(url, headers, params)
        if not data:
            break

        jobs = parse_data(data)
        if not jobs:
            break

        all_jobs.extend(jobs)

        # 增加延遲，避免過於頻繁的請求
        time.sleep(1)  # 1 秒延遲
        page += 1

        # 簡單的分頁停止條件 (抓取前 5 頁) - 可以根據需要調整
        if page > 5:
            print("🛑 已達到最大頁數，停止抓取")
            break

    print(f"✅ 總共抓到 {len(all_jobs)} 筆職缺資料")
    save_to_csv("static.csv", all_jobs)

if __name__ == "__main__":
    main()

