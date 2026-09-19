## SwartzCr/nekoatsume は Python製のコマンドラインゲーム

```
# 1. リポジトリをクローン
git clone https://github.com/SwartzCr/nekoatsume.git
cd nekoatsume

# 2. 実行
./nekoatsume.py
```

lib/update.py の修正
```
# 修正前（9行目付近）
from query import cats_in_yard, cats_not_in_yard

# 修正後
from .query import cats_in_yard, cats_not_in_yard
```

lib/display.py の修正（2箇所）
```
# 修正前（101行目付近）
if len(not_given) is 0:

# 修正後
if len(not_given) == 0:
```

```
# 修正前（118行目付近）
if len(data["pending_treasures"]) is 0:

# 修正後
if len(data["pending_treasures"]) == 0:
```

```
cd nekoatsume/lib

# itervalues -> values
sed -i 's/\.itervalues()/.values()/g' *.py

# iterkeys -> keys
sed -i 's/\.iterkeys()/.keys()/g' *.py

# iteritems -> items
sed -i 's/\.iteritems()/.items()/g' *.py
```
