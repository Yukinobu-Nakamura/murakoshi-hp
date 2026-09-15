#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
村越じゅんた 公式サイト — ACTIVITY セクション用 Facebook 最新投稿フィード更新スクリプト

やること:
  1. Facebook Graph API から対象ページの最新投稿を取得
  2. 写真つきの投稿を新しい順に 3 件選ぶ
  3. 写真を assets/img/fb/ にダウンロード(FaceBook CDN の URL は期限切れになるため)
  4. assets/data/facebook-latest.json を書き換える

使い方:
  export FB_PAGE_ID="＜FacebookページのID または ユーザー名＞"
  export FB_ACCESS_TOKEN="＜ページアクセストークン(長期)＞"
  python3 tools/update_facebook_feed.py

前提(重要):
  Facebook Graph API で投稿一覧を取得できるのは「Facebookページ」だけです。
  個人プロフィール(個人アカウント)の投稿は、本人であっても API では取得できません。
  個人プロフィールの場合は、Facebookページを作成するか、
  assets/data/facebook-latest.json を手で更新する運用にしてください。

終了コード:
  0 = 更新した / 2 = 設定不足 / 1 = 取得失敗(JSONは書き換えない)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GRAPH_VERSION = "v21.0"
WANTED = 3
FETCH_LIMIT = 25
TIMEOUT = 30

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "assets" / "data" / "facebook-latest.json"
IMG_DIR = ROOT / "assets" / "img" / "fb"
IMG_REL = "assets/img/fb"          # index.html から見た相対パス
PAGE_URL = "https://www.facebook.com/JuntaMurakoshi"

UA = "murakoshi-hp-feed-updater/1.0 (+https://www.facebook.com/JuntaMurakoshi)"


def die(msg: str, code: int = 1) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return json.loads(res.read().decode("utf-8"))


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        data = res.read()
    if len(data) < 1024:
        raise ValueError(f"画像が小さすぎます({len(data)} bytes): {url}")
    dest.write_bytes(data)


def excerpt(message: str, limit: int = 78) -> str:
    """投稿本文を1行の抜粋にする。改行は詰め、長すぎる場合は省略記号をつける。"""
    text = " ".join((message or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def main() -> None:
    page_id = os.environ.get("FB_PAGE_ID", "").strip()
    token = os.environ.get("FB_ACCESS_TOKEN", "").strip()
    if not page_id or not token:
        die(
            "FB_PAGE_ID と FB_ACCESS_TOKEN を環境変数に設定してください。\n"
            "        (Facebookページのみ対応。個人プロフィールはAPI取得不可)",
            code=2,
        )

    params = urllib.parse.urlencode(
        {
            "fields": "id,message,created_time,permalink_url,full_picture",
            "limit": str(FETCH_LIMIT),
            "access_token": token,
        }
    )
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{urllib.parse.quote(page_id)}/posts?{params}"

    try:
        payload = get_json(url)
    except Exception as exc:  # noqa: BLE001
        die(f"Graph API の取得に失敗しました: {exc}")

    if "error" in payload:
        die(f"Graph API がエラーを返しました: {payload['error']}")

    with_photo = [p for p in payload.get("data", []) if p.get("full_picture")]
    if not with_photo:
        die("写真つきの投稿が見つかりませんでした。JSONは変更していません。")

    IMG_DIR.mkdir(parents=True, exist_ok=True)

    posts = []
    for idx, post in enumerate(with_photo[:WANTED], start=1):
        filename = f"post-{idx}.jpg"
        try:
            download(post["full_picture"], IMG_DIR / filename)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] 画像のダウンロードに失敗しました({post.get('id')}): {exc}", file=sys.stderr)
            continue
        posts.append(
            {
                "image": f"{IMG_REL}/{filename}",
                "date": post.get("created_time"),
                "text": excerpt(post.get("message", "")),
                "permalink": post.get("permalink_url") or PAGE_URL,
                "alt": "Facebookに投稿された村越じゅんたの活動写真",
            }
        )

    if not posts:
        die("画像を1件も取得できませんでした。JSONは変更していません。")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(
            {
                "_readme": OUT_JSON.exists()
                and json.loads(OUT_JSON.read_text(encoding="utf-8")).get("_readme")
                or "Facebook最新投稿3件(自動生成)",
                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "source": PAGE_URL,
                "posts": posts,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"[OK] {len(posts)} 件を書き出しました → {OUT_JSON.relative_to(ROOT)}")
    for p in posts:
        print(f"     - {p['date']} {p['image']}")


if __name__ == "__main__":
    main()
