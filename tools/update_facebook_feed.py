#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
村越じゅんた 公式サイト — ACTIVITY セクション用 Facebook 最新投稿フィード更新スクリプト

やること:
  1. Facebook Graph API から対象ページの最新投稿を取得
  2. 「本人が自分で写真を投稿したもの」だけに絞り、新しい順に 3 件選ぶ
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

法務上の制約(2026-10-12 legal-officer レビュー指摘への対応):
  - リンクのシェア投稿では full_picture がリンク先記事の画像(＝第三者の著作物)になる。
    これを自サーバーへ複製して配信すると著作権法21条・23条の問題になるため、
    ALLOWED_STATUS_TYPES / ALLOWED_MEDIA_TYPES で「自前の写真投稿」だけに限定する。
    判定材料が取得できなかった投稿は、安全側に倒して除外する。
  - 写真への第三者の写り込みは機械判定できない。そのため本スクリプトの出力は
    staging ブランチにのみ反映し、人が目視してから本番へ出す運用とする
    (.github/workflows/update-facebook-feed.yml 参照)。

終了コード:
  0 = 更新した / 0 = 変更なし / 2 = 設定不足 / 1 = 取得失敗(JSONは書き換えない)
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

# 「本人が自分で投稿した写真/動画」とみなす種別。シェア(shared_story)は含めない。
ALLOWED_STATUS_TYPES = {"added_photos", "added_video", "mobile_status_update"}
# 添付の種別。link / share は第三者コンテンツの引き写しになるため除外する。
ALLOWED_MEDIA_TYPES = {"photo", "album", "video"}

# JPEG のマジックバイト(ファイル先頭の識別子)
JPEG_MAGIC = b"\xff\xd8\xff"

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "assets" / "data" / "facebook-latest.json"
IMG_DIR = ROOT / "assets" / "img" / "fb"
IMG_REL = "assets/img/fb"          # index.html から見た相対パス
PAGE_URL = "https://www.facebook.com/JuntaMurakoshi"

UA = "murakoshi-hp-feed-updater/1.0 (+https://www.facebook.com/JuntaMurakoshi)"

README_NOTE = (
    "ACTIVITYセクションに表示するFacebook最新投稿3件。"
    "tools/update_facebook_feed.py が自動で書き換える。"
    "posts が空の間は index.html に書かれた既定の3カードがそのまま表示される(表示は崩れない)。"
    "本人が自分で投稿した写真のみを対象とし、リンクや他者投稿のシェアは除外している。"
)


def die(msg: str, code: int = 1) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def get_json(url: str, token: str) -> dict:
    # アクセストークンはURLではなくヘッダで渡す。
    # URLに乗せると、Meta側のアクセスログや中間プロキシ、例外メッセージに残りうるため。
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return json.loads(res.read().decode("utf-8"))


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        data = res.read()
    if len(data) < 1024:
        raise ValueError(f"画像が小さすぎます({len(data)} bytes): {url}")
    if not data.startswith(JPEG_MAGIC):
        raise ValueError("JPEG ではないデータが返りました(拡張子と中身が食い違うため中止)")
    dest.write_bytes(data)


def excerpt(message: str, limit: int = 78) -> str:
    """投稿本文を1行の抜粋にする。改行は詰め、長すぎる場合は省略記号をつける。"""
    text = " ".join((message or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def is_own_photo_post(post: dict) -> bool:
    """本人が自分で写真を投稿したものか。判定できない場合は安全側に倒して False。"""
    if not post.get("full_picture"):
        return False

    status_type = post.get("status_type")
    media_types = {
        att.get("media_type")
        for att in (post.get("attachments", {}) or {}).get("data", [])
        if att.get("media_type")
    }

    # 添付の種別が取れていれば、それを最優先で判定する(link / share はここで落ちる)
    if media_types:
        return bool(media_types & ALLOWED_MEDIA_TYPES) and not (media_types - ALLOWED_MEDIA_TYPES)

    # 添付が取れない場合は status_type で判定する
    if status_type:
        return status_type in ALLOWED_STATUS_TYPES

    # どちらも判定材料が無ければ採用しない
    return False


def load_existing_ids() -> list:
    """既存JSONに入っている投稿IDの並びを返す(無ければ空)。"""
    if not OUT_JSON.exists():
        return []
    try:
        data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    return [p.get("id") for p in data.get("posts", []) if isinstance(p, dict)]


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
            "fields": (
                "id,message,created_time,permalink_url,full_picture,"
                "status_type,attachments{media_type,type}"
            ),
            "limit": str(FETCH_LIMIT),
        }
    )
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{urllib.parse.quote(page_id)}/posts?{params}"

    try:
        payload = get_json(url, token)
    except Exception as exc:  # noqa: BLE001
        die(f"Graph API の取得に失敗しました: {exc}")

    if "error" in payload:
        die(f"Graph API がエラーを返しました: {payload['error']}")

    all_posts = payload.get("data", [])
    eligible = [p for p in all_posts if is_own_photo_post(p)]
    skipped = len(all_posts) - len(eligible)
    if skipped:
        print(f"[INFO] 自前の写真投稿でない {skipped} 件を除外しました(シェア・リンク等)")
    if not eligible:
        die("対象となる写真つきの自前投稿が見つかりませんでした。JSONは変更していません。")

    selected = eligible[:WANTED]
    new_ids = [p.get("id") for p in selected]

    # 中身が前回と同じなら、JSONも画像も書き換えない。
    # (updated の日時だけ変えて毎日コミットが積まれるのを防ぐ)
    if new_ids == load_existing_ids() and all(
        (IMG_DIR / f"post-{i}.jpg").exists() for i in range(1, len(selected) + 1)
    ):
        print("[OK] 前回と同じ投稿のため、変更はありません。")
        return

    IMG_DIR.mkdir(parents=True, exist_ok=True)

    posts = []
    for idx, post in enumerate(selected, start=1):
        filename = f"post-{idx}.jpg"
        try:
            download(post["full_picture"], IMG_DIR / filename)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] 画像のダウンロードに失敗しました({post.get('id')}): {exc}", file=sys.stderr)
            continue
        posts.append(
            {
                "id": post.get("id"),
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
                "_readme": README_NOTE,
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
