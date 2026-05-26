import json
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from xml.etree import ElementTree

import requests

RSS_URL = os.getenv("NEWS_RSS_URL", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "10"))
TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT", "20"))
NEWS_ARCHIVE_DIR = os.getenv("NEWS_ARCHIVE_DIR", "news_archive")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")


def fetch_titles(rss_url: str, max_items: int) -> list[tuple[str, str]]:
    response = requests.get(rss_url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()

    root = ElementTree.fromstring(response.content)
    channel = root.find("channel")
    if channel is None:
        return []

    items = []
    for item in channel.findall("item")[:max_items]:
        title = (item.findtext("title") or "(無標題)").strip()
        link = (item.findtext("link") or "").strip()
        items.append((title, link))

    return items


def save_titles(items: list[tuple[str, str]], archive_dir: str) -> Path:
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_file = archive_path / f"news_{timestamp}.json"

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rss_url": RSS_URL,
        "count": len(items),
        "items": [{"title": title, "link": link} for title, link in items],
    }

    output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_file


def build_email_body(items: list[tuple[str, str]], saved_file: Path) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not items:
        return f"每日新聞通知（{now}）\n\n今天沒有抓到新聞資料。\n存檔位置：{saved_file}"

    lines = [
        f"每日新聞通知（{now}）",
        "",
        "以下是今日抓取的新聞標題：",
        "",
    ]
    for idx, (title, link) in enumerate(items, start=1):
        lines.append(f"{idx}. {title}")
        if link:
            lines.append(f"   {link}")

    lines.extend(["", f"存檔位置：{saved_file}"])
    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    missing = [
        name
        for name, value in {
            "SMTP_HOST": SMTP_HOST,
            "SMTP_USERNAME": SMTP_USERNAME,
            "SMTP_PASSWORD": SMTP_PASSWORD,
            "EMAIL_FROM": EMAIL_FROM,
            "EMAIL_TO": EMAIL_TO,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"缺少必要環境變數: {', '.join(missing)}")

    message = MIMEMultipart()
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, [addr.strip() for addr in EMAIL_TO.split(',')], message.as_string())


def main() -> None:
    titles = fetch_titles(RSS_URL, MAX_ITEMS)
    saved_file = save_titles(titles, NEWS_ARCHIVE_DIR)
    subject = f"每日新聞通知 - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    body = build_email_body(titles, saved_file)
    send_email(subject, body)
    print(f"已寄出 {len(titles)} 則新聞，並存檔至 {saved_file}")


if __name__ == "__main__":
    main()
