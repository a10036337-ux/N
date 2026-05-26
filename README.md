# Daily News Mailer (GitHub Actions)

這個專案會透過 GitHub Actions 每日自動執行：
1. 爬取新聞 RSS 標題
2. 將新聞標題整理後寄到你的 Email

## 檔案結構

- `.github/workflows/daily-news-mail.yml`：排程與執行流程
- `scripts/daily_news_mailer.py`：爬新聞與寄信程式

## 需要設定的 GitHub Secrets

請在 GitHub Repo → **Settings** → **Secrets and variables** → **Actions** 新增：

- `NEWS_RSS_URL`（可選，預設為 Google 新聞繁中 RSS）
- `MAX_ITEMS`（可選，預設 `10`）
- `NEWS_ARCHIVE_DIR`（可選，預設 `news_archive`，用來儲存每日抓取結果 JSON 檔）
- `SMTP_HOST`（例如 `smtp.gmail.com`）
- `SMTP_PORT`（例如 `587`）
- `SMTP_USERNAME`
- `SMTP_PASSWORD`（若為 Gmail 建議用 App Password）
- `EMAIL_FROM`
- `EMAIL_TO`（可多人，用逗號分隔）

## 觸發方式

- 自動：每天 UTC 00:00（台灣時間 08:00）
- 手動：到 Actions 頁面執行 `Daily News Mailer`

## 注意事項

- GitHub Actions 只能在雲端執行與寄信，無法替你「從這個對話環境直接 push 到你的 GitHub」；你需要把目前分支推到遠端，或在 GitHub 上建立這些檔案。
- 若 SMTP 服務商有額外安全限制，請先完成授權設定。


## 新聞存檔功能

- 每次執行會將新聞標題與連結存成 JSON 檔，預設放在 `news_archive/`。
- 檔名格式：`news_YYYYMMDDTHHMMSSZ.json`（UTC 時間）。
- 你可以透過 `NEWS_ARCHIVE_DIR` secret 調整存檔資料夾。
