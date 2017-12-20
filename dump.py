#! /usr/bin/env python
# -*- coding:utf-8 -*-

import json
import qiita

o = qiita.adventCalendar(2017)
rows = o.findCalendarListAll(with_item=True, with_count_hatena_bookmark=True)

print json.dumps(rows, ensure_ascii=False).encode('utf_8')
