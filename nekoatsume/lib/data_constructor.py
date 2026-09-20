import json
import os
import time
import datetime


def store_data(data):
    data_file = os.getcwd() + '/var/data.json'
    with open(data_file, 'w') as f:
        json.dump(data, f)


def build_data():
    cur_time = time.time()
    data = {}
    data["items"] = {}
    data["cats"] = {}
    data["yard"] = []
    data["owned_food"] = []
    data["space"] = 6
    data["food_remaining"] = 0
    data["food"] = ""
    data["prefix"] = ""
    data["g_fish"] = 10
    data["s_fish"] = 300
    data["seen_cats"] = []
    data["start"] = cur_time
    data["pending_money"] = []
    data["pending_treasures"] = []
    build_items(data)
    build_cats(data)
    store_data(data)


def make_item(name, cost, cur, size, desc):
    return {"cost": cost,
            "currency": cur,
            "description": desc,
            "attributes": [],
            "occupant": [],
            "occupied": False,
            "in_yard": False,
            "size": size,
            "name": name}


# TODO: Keep data in JSON file to simplify this function
#       Consider something like Marshmallow for deserialization into app objs
#       https://marshmallow.readthedocs.org/en/latest/
# TODO: add a section to each item that is a list of actions that a cat can take
#       on it. Maybe there can be some static lists per type of item. Such as
#       climbable = ["is on top of", "is clawing at", "is jumping off of"]
#       then add that to the end of each item
#
# 日本語化メモ: アイテム名はそのまま辞書のキーにもなる。名前を変えると
# 既存の var/data.json とは互換性がなくなるので、その場合は data.json を削除して新規開始すること。
def build_items(data):
    items = [
        ("ゴムボール", 5, "s", 1, "小さな明るいオレンジ色のゴムボール。ふにふにで、ピコピコ鳴るよ!"),
        ("キラキラボール", 5, "g", 1, "きらめくラメが入った、小さな透明のゴムボール!"),
        ("毛糸玉", 10, "s", 1, "赤い毛糸玉だよ!"),
        ("高級毛糸玉", 15, "g", 1, "赤・青・緑に銀色の糸がきらめく、高級な毛糸玉!"),
        ("テニスボール", 25, "s", 1, "毛羽立った鮮やかな黄色のテニスボール!"),
        ("紙袋", 20, "s", 1, "スーパーの紙袋。ガサガサいい音がするよ!"),
        ("爪とぎポール", 5, "g", 1, "猫がバリバリ爪をとげる、いい感じのポール!"),
        ("高級爪とぎポール", 15, "g", 1, "硬い木と合成皮革でできた、デラックスな爪とぎポール!"),
        ("金魚鉢", 10, "g", 1, "かわいい金魚が泳ぐ小さな金魚鉢!"),
        ("小型キャットハウス", 75, "s", 3, "少しだけカーペット張りの小さなキャットハウス。3匹まで入れるよ!"),
        ("中型キャットハウス", 150, "s", 5, "全面カーペット張りの中くらいのキャットハウス。5匹まで入れるよ!"),
        ("大型キャットハウス", 50, "g", 7, "高級ベルベル絨毯に手縫いの仕上げ、7匹まで入れる大きなキャットハウス!"),
        ("マタタビの袋", 7, "g", 1, "小さなマタタビの袋。においで猫が大興奮!"),
        ("無地のクッション", 30, "s", 1, "青くてやわらかい、小さな無地のクッション!"),
        ("絞り染めのクッション", 15, "g", 1, "絞り染めのフリースでできた、ふかふかの厚いクッション!"),
        ("プラスチックのバケツ", 20, "s", 1, "白い取っ手のついた小さな緑のバケツ。バケツがあるぞ!"),
        ("シリアルの箱", 15, "s", 1, "「シナモンとろけるゴロゴロ」の空き箱!"),
        ("果物の箱", 75, "s", 1, "小さな段ボールの果物箱。入れそうなら、入っちゃう!"),
        ("大きな箱", 30, "g", 4, "もとは家電が入っていた大きな段ボール箱。猫が4匹まで入れるよ!"),
        ("蝶々のおもちゃ", 15, "g", 1, "長い棒の先の糸に蝶々がぶら下がった、かわいいおもちゃ。ひらひら楽しい!"),
        ("ロボットレーザーポインター", 125, "g", 1, "レーザーポインターを持った小さなロボットアーム。みんな大好き!"),
        ("虹色の傘", 25, "g", 5, "虹色もようの大きな傘。猫が5匹まで入れるよ!"),
        ("無地の傘", 250, "s", 4, "明るい黄色の大きな無地の傘。猫が4匹まで入れるよ!"),
        ("カエルのぬいぐるみ", 75, "s", 1, "ぎゅっとすると鳴く、緑のかわいいカエルのぬいぐるみ!"),
        ("ドライフード", 10, "s", 300, "ごく普通のドライフード。カリカリでシンプルな味。"),
        ("ウェットフード缶", 2, "g", 300, "ごく普通のウェットフード。においが強烈!"),
        ("高級フード缶", 5, "g", 300, "職人が手づくりした、フェアトレードのオーガニック猫ごはん。んー、おいしい!"),
    ]
    for name, cost, cur, size, desc in items:
        data["items"][name] = make_item(name, cost, cur, size, desc)


def make_cat(name, desc, treasure, mod, time_limit=30, entry_chance=0.1, exclusive=False, fav_toy="", strength=5):
    return {"name": name,
            "desc": desc,
            "time_in_yard": 0,
            "total_time_in_yard": 0,
            "on_toy": {},
            "in_yard": False,
            "treasure": treasure,
            "given_treasure": False,
            "time_limit": time_limit,
            "entry_chance": entry_chance,
            "fav_toy": fav_toy,
            "exclusive": exclusive,
            "strength": strength,
            "mod": mod}


# TODO: Keep data in JSON file to simplify this function
#       Consider something like Marshmallow for deserialization into app objs
#       https://marshmallow.readthedocs.org/en/latest/
#
# TODO: should this be named birth_cats? ;)
def build_cats(data):
    data["cats"]["ゴードー"] = make_cat("ゴードー", "いつもあなたのごはんを食べにくる、いちばん手のかかる猫", "役に立たない木切れ(ゴードーだから)", 0.1)
    data["cats"]["プッカ"] = make_cat("プッカ", "プッカはクリーム色のぶちがある白い短毛で、緑の目の猫。レーザーを追いかけたり、サーフィンをするのが大好き", "サーフワックスのかたまり", 0.1)
    data["cats"]["ピーブルズ"] = make_cat("ピーブルズ", "ピーブルズは青い目の白黒の短毛猫。デスメタルとマタタビの山が好き", "べっ甲のギターピック", 0.1)
    data["cats"]["タラワ"] = make_cat("タラワ", "タラワは白い筋の入ったグレーの長毛で、灰色の目の猫。のんびりするのと、鳥を追いかけるのが好き", "アオカケスの羽根", 0.1, strength=6)
    data["cats"]["フェリックス"] = make_cat("フェリックス", "フェリックスはオレンジと白の短毛のトラ猫で、黄色い目。とてもおだやかで、一日中ほとんど瞑想している", "仏像のお香立て", 0.1)
