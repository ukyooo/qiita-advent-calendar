# Qiita Advent Calendar

Qiita Advent Calendar の [はてなブックマーク](http://b.hatena.ne.jp/) 数を取得

* see: https://qiita.com/ukyooo/items/5e23db46dbc1bbf0c2ed



## Usage

```
$ python dump.py > dump.json
```

### Data

| key           | type      | description                   |
|---------------|-----------|-------------------------------|
| url           | string    | カレンダーの URL              |
| code          | string    | カレンダーの識別子            |
| name          | string    | カレンダーの名称              |
| count         | integer   | カレンダーに対する はてブ数   |
| item[].url    | string    | 記事の URL                    |
| item[].user   | string    | 記事の投稿者                  |
| item[].title  | string    | 記事のタイトル                |
| item[].count  | integer   | 記事に対する はてブ数         |
| item[].domain | string    |                               |

```
$ cat dump.json | jq '.[]|select(.code == "ex-mixi")' ;
{
  "url": "https://qiita.com/advent-calendar/2017/ex-mixi",
  "code": "ex-mixi",
  "name": "ex-mixi"
  "count": 12,
  "item": [
    {
      "url": "http://masartz.hatenablog.jp/entry/2017/12/01/101612",
      "count": 74,
      "domain": "hatena.d.",
      "user": "masartz",
      "title": "昔やってたこと、今やってること、とかとかIntroduction "
    },
    {
      "url": "http://kakkablog.hatenadiary.jp/entry/2017/12/01/190151",
      "count": 14,
      "domain": "hatena.d.",
      "user": "KAKKA",
      "title": "スクラムとかAndroidとか音声認識とかに関して "
    },
    {
      "url": "http://kkinukawa.hatenablog.com/entry/2017/12/03/002951",
      "count": 13,
      "domain": "hatena.d.",
      "user": "k_kinukawa",
      "title": "Go書くぞおじさんになった話（あるいは\"射撃しつつ前進\"するためのスイッチの入れ方） "
    },
    ...
  ]
}


```

### Example

```
# カレンダー別 ランキング (各記事のはてブ数 + カレンダー自体のはてブ数)
$ cat dump.json \
    | jq -cr .[] \
    | jq -cr '[reduce .item[].count as $c (0; . + $c) + .count, .name, .url]|@tsv' \
    | sort -nr \
    | head -n 10 \
    | awk -F"\t" 'BEGIN {
        i = 0;
        print "| 順位  | はてブ数  | Qiita Advent Calendar 2017    |"
        print "|:-----:|----------:|-------------------------------|"
}
{
        i++;
        print "| " i " | " $1 " | [" $2 "](" $3 ") |";
}' ;
```

```
# 記事別 ランキング
$ cat dump.json \
    | jq -cr .[] \
    | jq -cr '{ name: .name, url: .url, item: .item[] }' \
    | jq -cr '[.item.count, .name, .url, .item.title, .item.url]|@tsv' \
    | sort -nr \
    | head -n 10 \
    | awk -F"\t" 'BEGIN {
        i = 0;
        print "| 順位  | はてブ数  | Qiita Advent Calendar 2017    | タイトル   |"
        print "|:-----:|----------:|-------------------------------|------------|"
} {
        i++;
        print "| " i " | " $1 " | [" $2 "](" $3 ") | [" $4 "](" $5 ") |";
}' ;
```

