# 村越じゅんた 公式サイト

作成: 2026-09-14 / 発注: 中村さん(再生の道つながりの制作依頼・本人承諾済み)
**採用案: 04 Warm Sincere**(2026-09-15 決定。ルート index.html を本案に差し替え済み)
**公開URL**: https://yukinobu-nakamura.github.io/murakoshi-hp/

## 構成
```
index.html              … ★本サイト(採用案04)。showcase.html から昇格
showcase.html           … 旧ショーケース(11案タブ切替+PC/スマホ幅トグル)。比較用に保存
patterns/pattern-00.html … 04案の提案時ファイル(index.html と同内容・相対パスのみ差異)
patterns/pattern-01〜11.html … 残り10案(単一HTML自己完結。04は欠番=pattern-00が04枠)
assets/css/style.css    … CSS(デザイントークン+レスポンシブ+PC基準倍率)
assets/js/main.js       … JS(依存ゼロ。FBフィード取込・YouTubeサムネ再生を含む)
assets/img/             … WebP画像(全て本人SNS由来+favicon/OGPは生成)
assets/img/fb/          … Facebook投稿写真(更新スクリプトが自動保存)
assets/data/facebook-latest.json … ACTIVITY表示用のFB最新投稿3件
tools/update_facebook_feed.py … 上記JSONを Graph API から更新するスクリプト
CONTENT_SPEC_MURAKOSHI_C1.md … 文言・素材・法務対応の正本
PATTERNS_SPEC.md        … 11案制作の共通仕様(文言固定・禁止語・検収基準)
_sources/               … 元画像(git管理外)
```

## 2026-09-15 の修正(中村さん指示・8項目)
1. 「府中に、むちゅう。」と「村越じゅんた」を同一サイズに統一(`--hero-type` で一元管理)
2. PC表示をブラウザズーム150%相当に固定(`:root{zoom}` を画面幅で段階適用。1024px以下は従来どおり各幅最適)
3. ACTIVITY を Facebook 最新投稿3件の自動表示に変更(下記「Facebook連携」参照)
4. PROFESSION の動画を、再生の道公式の紹介動画サムネイル表示 → クリックで再生に変更
5. 本文のサブテキスト色を濃く(`--ink-soft` #6f6862 → #4e4741。コントラスト比 約7.8:1)
6. 「家電寄贈の、お願い。」→「寄贈のお願い。」(ナビ・本文・フッターの全4箇所)
7. SNSアイコンをバナー(ヘッダー)の「村越じゅんた」ロゴの隣に追加
   - 狭い端末(480px以下)では英字サブ「MURAKOSHI JUNTA」を畳み、アイコンを詰めて1行を維持する
8. フッターの「掲載の写真は本人のSNSで公開したものを…」の一文を削除

### 検証(2026-09-15)
- 画面幅 320/360/390/430/480/600/768/1024/1025/1149/1150/1398/1399/1400/1600/1920/2560 で横オーバーフロー **0**
- 見出しと氏名のフォントサイズ一致を全幅で機械確認、倍率の切替に隙間なし(min-width積み上げ方式)
- ヘッダーのロゴ折返し・SNSアイコンとハンバーガーの衝突を全幅で機械確認(320pxでも1行を維持)
- YouTubeサムネ→iframe差し替えの動作確認済み / コンソールエラー 0
- FBフィードは実データを投入して3カードの描画・日付・リンク・画像読込を確認後、空に戻した

## Facebook連携(ACTIVITY)
`assets/data/facebook-latest.json` の `posts` を読んで3カードを描画する。
取得できない場合は index.html に書かれた既定の3カードをそのまま表示するため、**表示が崩れることはない**。

```bash
export FB_PAGE_ID="＜FacebookページID＞"
export FB_ACCESS_TOKEN="＜長期ページアクセストークン＞"
python3 tools/update_facebook_feed.py     # 写真をDLしJSONを更新
```

✅ 2026-09-15、村越さんのFacebookは**Facebookページ**と確認。Graph API での自動更新が可能。

### 完全自動化(GitHub Actions)の手順
`.github/workflows/update-facebook-feed.yml` を用意済み。毎日 06:00 JST に取得して自動コミットする。
**Secrets を登録するまでは自動でスキップ**されるので、放置してもエラーにはならない。

1. Meta for Developers でアプリを作成 → 対象のFacebookページを紐づける
2. **長期のページアクセストークン**を発行(権限: `pages_read_engagement` / `pages_show_list`)
3. GitHubリポジトリの Settings → Secrets and variables → Actions に登録
   - `FB_PAGE_ID` … FacebookページのID(または `JuntaMurakoshi`)
   - `FB_ACCESS_TOKEN` … 上記2のトークン
4. Actions タブから "Facebook最新投稿の取り込み" を手動実行して動作確認

⚠️ アプリ作成とトークン発行は**村越さん側のFacebookアカウントで行う必要がある**(こちらでは代行しない)。
⚠️ トークンには有効期限がある。失効するとJSONが更新されなくなるが、
   その場合も**既定の3カードが表示されるだけでサイトは壊れない**。

## 11案の検収記録(2026-09-14)
- 全11ファイルで機械検収 ALL PASS: 禁止語0・必須注記2種完全一致・noindex・絵文字0・外部ドメイン正常
- 全案の文言・写真・注記は pattern-00(legal-officerレビュー済み)から固定転記。レイアウト骨格のみ別物
- ショーケースの全タブ切替・iframeロードを機械確認済み
- 採用案決定後は、そのパターンをルートindex.html化+noindex解除+OGP絶対URL化して本公開する

## デザイン
- hp-design-proposal(11パターン)の DESIGN_KATA_C1.md 15ルール+E章トークン規律を適用
- 型: 非対称分割ヒーロー(河野型・写真70vh・下端接地)× ストーリーテリング(Warm Earth)× 市民向けの分かりやすさ(Civic Blue)
- 3色: 地 #faf8f4 / 墨 #272220 / アクセント #5b48b5(再生の道の紫を誠実トーンに)
- 書体: Zen Old Mincho(見出し=誠実)+ Zen Kaku Gothic New(本文=親しみ)
- キャッチ「府中に、むちゅう。」は本人のX表示名「府中にむちゅう」由来

## 検証済み
- 4幅(390/768/1024/1440)で横オーバーフロー0・文字×写真の被り0(可視要素の矩形交差検査)
- 画像破損0 / コンソールエラー0
- prefers-reduced-motion 対応・フォーカスリング・aria(ハンバーガー/SNSラベル)

## 法務(legal-officer レビュー 2026-09-14・要修正5件は全て対応済み)
- 公選法129条(事前運動)適合: 選挙/投票/立候補等の語ゼロ。政治活動用サイトの注記あり
- 再生の道公式サムネ掲載→ YouTube公式埋め込み(youtube-nocookie)に差し替え+「党公式サイトではない」フッター注記
- NPO寄贈導線は「家電寄贈のお願い」に改題+「政治活動への寄附ではない」注記強化
- 通行人が写るサムネは差し替え済み(人物写り込みゼロ)

## 納品範囲(2026-09-15 確定)
- **こちらの担当はステージングまで**。GitHub Pages に置いた版を村越さん側が確認する。
- **本番サーバーへのアップは村越じゅんた氏ならびにその後援会組織が実施**。DNS・サーバー契約には関与しない。

## 本番アップ時の引き継ぎ(村越さん・後援会側の作業)
1. **noindex を外す** — `index.html` 6行目の
   `<meta name="robots" content="noindex, nofollow">` を**削除**する。
   これは「検索エンジンに登録しないで」という指示タグで、ステージング版が
   Google等に載って本番と二重に表示されるのを防ぐために入れてある。本番では必ず外す。
2. **OGP を本番の絶対URLにする** — `og:image` と `og:url` を
   `https://本番ドメイン/assets/img/ogp.png` のような絶対URLに書き換える
   (SNSでシェアしたときのサムネイル表示に必要)。
3. ファイル一式(`index.html` + `assets/`)をサーバーの公開ディレクトリへアップ。
   `showcase.html` `patterns/` `tools/` `_sources/` `*.md` は**本番不要**。

## ⚠️ 残確認(村越さん本人へ)
1. 会社の登記上の地位の確認(「設立に加わり、取締役として」の表記で整合させたが、代表取締役なら表記を戻せる)
2. ~~写真の著作権~~ → **2026-09-15 クローズ**。本人からの制作依頼であり写真利用の許諾も取得済み。
   これに伴いフッターの出所注記を削除(CONTENT_SPEC / PATTERNS_SPEC に記録済み)。
3. ~~Facebookの種別~~ → **2026-09-15 クローズ**。**Facebookページ**と確認。Graph API での自動更新が可能。

## プレビュー
ローカル: `python3 -m http.server 8749` → http://127.0.0.1:8749/
(bgrun「村越HPプレビュー用ローカルサーバー」で起動中)
