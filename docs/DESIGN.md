
# 工数管理・集計アプリ Active Task Summary

## 目的

- 実施した作業の効率と金銭的な支出を把握するため
- 解析結果から、より効率的な時間の使い方をするため

## 機能

- ログイン機能
  - ローカルアカウントモード
  - LDAP連携モード
- グループ機能
  - ユーザを複数のグループに所属できるようにする
  - 作業単位と管理単位に分けて考えるため
- 工数入力機能
  - どのプロジェクトで何の作業を何時間したかを入力する
  - 入力後に修正できること
  - ただし、確定処理（締め）の後は編集できない
- 工数集計機能
  - グループ単位で集計することができる
    - ユーザもグループとして扱うことにする（自分しか所属していない）
    - どのグループが集計可能か、に帰結することができる
- 作業マスタ編集
  - プロジェクトを作成する
  - １つのプロジェクトで複数の作業マスタを作成できる
    - エンジニアと営業でマスタが違うため
    - ユーザには複数のマスタを割り当てることも可能(技術と営業を兼務など)
  - 作業マスタの作成（テンプレート）
    - まずはテンプレートを作成する。
  - 作業マスタの作成（本当の作業マスタ）
    - テンプレートから新規に作成できる
      - かならず何かのテンプレートから派生する必要がある
      - デフォルトテンプレート（＝空）を用意して対応
    - 一度作った作業マスタにテンプレートのデータをマージできる
      - 作業一覧が不足して後から追加になってもテンプレート直せばよい
      - 自動反映はしない。手動で行う。
    - ID値とsortkeyを用意し表示順を変更できるようにする
- システム管理機能
  - パスワード変更
    - ローカルアカウントモードの場合のみ
    - 全員が可能
  - ユーザアカウント編集
    - ローカルアカウントの追加
    - 現在のシステムデータベースのユーザ一覧と権限の変更

## 詳細設計

- ローカルアカウントモードとLDAP連携モード
  - ローカルアカウントモードは常に有効（adminアカウントのこと）
- 制限について
  - 工数データ入力
    -  全員にある
    - 自分の所属するプロジェクトにつけることが可能
  - 参照と集計
    - 自分のみ
    - 自分が所属するグループのみ(小グループ)
    - 自分の所属する部署のみ(大グループ)
    - すべて集計可能
  - 作業マスタの作成・編集・削除
  - システムのログインアカウント編集
    - ローカルアカウントモード
    - LDAPとの連携により、初回ログイン成功時にユーザを作成
- 工数集計について
  - データベース設計
    - スキーマ概念
      - ユーザ、プロジェクト、作業グループ、作業細目の関係
      - ユーザは所属するjobを決めておく
      - 開発職、営業職、運用職、管理職、間接
```
user
  |-project
    |-job
      |-task
      |-task
      |-task
  |-project
    |-job
      |-task
      |-task
      |-task
------------------
user : project = 1:N
project : job = 1:N
job : task = 1:N
-------------------
テンプレート登録機能が必要なのは、jobに対応するtask群。
```
  - user.relate_attr
    - ユーザ自身の属性
```
|| カラム名 || データ型 || DB属性 || データ内容 || 備考 ||
|| user_id ||  ||  ||  ||  ||
|| expire_dt ||  || date || 
|| accounttype ||  || int ||  || 0:local,1:LDAP ||
  - project
    - プロジェクトです。これが仕事の一番大きなくくりになります
|| カラム名 || データ型 || DB属性 || データ内容 || 備考 ||
|| id ||  ||  ||  ||  ||
|| name ||  ||  ||  ||  ||
|| start_dt ||  ||  ||  || 未入力の場合は工数登録できない ||
|| end_dt ||  ||  ||  || NULLの場合は未完了 ||
```
  - job
    - 仕事の種別（開発、運用、営業、管理、間接などの仕事タイプ）
```
|| カラム名 || データ型 || DB属性 || データ内容 || 備考 ||
|| id ||  ||  ||  ||  ||
|| name ||  ||  ||  ||  ||
  - task
    - 作業細目
|| id ||  ||  ||  ||  ||
|| name ||  ||  ||  ||  ||
|| job_id  ||  ||  ||  ||  ||
|| sortkey ||  ||  ||  || 表示するときの順序（昇順） ||
```
  - projectworker
```
|カラム名 || データ型 || DB属性 || データ内容 || 備考 ||
|| id ||  ||  ||  ||  ||
|| project_id ||  ||  ||  ||  ||
|| user_id ||  ||  ||  ||  ||
```
  - usedtasktime
    - 作業時間データ
    - 誰が、いつ、何のプロジェクトで、何の作業を、何分したか
    - このテーブルはかなりのレコード数になる。
      - 1日に[人xtask]の分だけレコードができる
      - 400人x4taskの場合、1600レコード
      - 一年で、1600x245=392000レコード
      - 終了したプロジェクトはテーブルを移すとか考える。
        - 終了したあと、やっぱり継続、とかある。
      - 運用系や事務仕事といった終わらないプロジェクトがある
        - よって、「終了した」という条件で別テーブルに移動は無理
        - 年ごとにテーブルを分ける実装を考える
          - indexはあるので信用するか。
    - 検索パターン（indexの付与）
      - ある期間の集計（日次、月次、年次、プロジェクト実施中）
        - プロジェクトと日付の範囲で集計する
        - project_idとtaskdateの複合index
      - 誰がどの作業をどれだけやっているか
        - プロジェクトを横断した作業レポートがほしい場合
        - グループでほしい場合はuser_idを複数or検索する
        - user_idとproject_idの複合index
```
|| カラム名 || データ型 || DB属性 || データ内容 || 備考 ||
|| id || bigint || pkey ||  ||  ||
|| user_id || int ||  ||  ||  ||
|| project_id || int ||  ||  ||  ||
|| task_id || int ||  ||  ||  ||
|| taskdate || date ||  ||  ||  ||
|| tasktime || time ||  ||  ||  ||
```


## 画面及びurl設計

- /mountname/appname
  - login
  - top
  - regist
    - /project_id/user_id/yyyymmdd/
    - /project_id/user_id/yyyymm/  これの実装は必要になったら考える
  - summary
    - project
      - 全体の作業時間
      - どのjobのどのtaskをどのくらいしたか（作業者全員の合算値）
    - job
      - 全体の作業時間
      - どのjobのどのtaskをどのくらいしたか（作業者全員の合算値）
    - user
    - /project_id/
        - プロジェクトの開始から現在までの合計値
    - /project_id/yyyymmdd_yyyymmdd/
      - from to 方式で日付を入れる
      - プロジェクトの年突き合計値
    - /project_id/yyyymmdd_yyyymmdd/u<user_id>/
      - ある人の作業時間
    - /project_id/yyyymmdd_yyyymmdd/j<ob_id>/
      - 所属するジョブグループの累積値
      - 開発者全体や運用者全体、営業全体を示す
  - api
    - ajax処理を行うためのjson受付インタフェース
    - パラメータ
```
{'project_id': number,
 'from date': string,
 'to date': string,
 'job_id' : [number, number,...],
 'user_id': [number, number,...],
 'fetch_one': number,
}
```
  - manage
    - user
      - id
        - edit/
    - project
    - task
    - job
    - notify
      - 数字をみて、警告やアラートを飛ばバッチ処理の登録
      - 決めた工数時間に達するとお知らせ
      - ある日付までに工数時間が達しないとお知らせ
      - ほかにアイデアがあれば


## 実装方法

- webアプリとする
- djangoを使ったwsgiアプリ
- データベースはdjangoがサポートするものはひと通り使える
  - テストや個人的な利用はsqlite3
  - 本番運用はpostgresqlがおすすめ。理由は検索時のインデックス
- 作業時間が入るテーブルはレコード数が多くため、対策を講じる
  - 服数列のインデックスを生成し、検索性能を維持する
  - 集計処理はヒットするレコード件数が多いことが予想される
  - そのため、ajaxな画面表示実装を行う
  - 検索処理を行うajax処理を行うapiのようなページを用意する
  - ブラウザはjavascriptにより、ユーザの要求をAPI単にに分割してリクエストを繰りして順次画面を更新する


## グループ機能の設計

- 現在の実装ではグループ機能は以下がある
  - projectworker : 作業目的によるグルーピング機能
  - job : 職種によるグルーピング機能
- グルーピング機能はロールをプリセット機能とする
  - そのため、グループ名に意味はない
- ただし、superuserは全ロール機能をもつこととする
  - roleテーブルはない
  - プログラムとして値を持つ必要があるため埋め込む
  - プログラムの埋め込んだ値がroleidとなる
- テーブル構成
  - auth_user
  - Project
  - ProjectWorker (=project worker)
    - id
    - project_id
    - job_id
    - user_id

## ロール機能

- パスワード変更
- マスタデータの追加
- マスタデータの変更・削除
- ロール設定の変更