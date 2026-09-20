"""
Place items.

This module handles the placement of food and toys in the yard.
"""

from lib import printer

try:
    input = raw_input
except NameError:
    pass


def get_choice(options, prompt, prefix):
    """
    番号または名前で選択を受け付ける共通関数。
    
    options: [(key, display_name), ...] のリスト
    戻り値: 選ばれた key、または None（キャンセル/無効）
    """
    if len(options) == 0:
        printer.warn(prefix, "選べるものがありません!")
        return None

    # 番号付きで表示
    for i, (key, name) in enumerate(options, 1):
        printer.yard(prefix, "{0}. {1}".format(i, name))
    
    raw = input("{.YARD}{}{.ENDC} {} ".format(
        printer.PColors, prefix, printer.PColors, prompt))
    
    # ENTERだけならキャンセル
    if raw.strip() == "":
        return None
    
    # 番号入力かどうか
    try:
        idx = int(raw.strip())
        if 1 <= idx <= len(options):
            return options[idx - 1][0]
    except ValueError:
        pass
    
    # 文字入力（大文字小文字は無視。名前でも表示名でもマッチ）
    raw_norm = raw.strip().lower()
    
    for key, name in options:
        if raw_norm == key.lower() or raw_norm == name.lower():
            return key
    
    printer.warn(prefix, "その選択肢はわかりませんでした")
    return None


def menu(data):
    """Display yard menu."""
    data["prefix"] = printer.PREFIX_YARD
    list_yard_items(data)
    data["in_yard"] = True
    
    actions = [
        ("list owned items", "持っているアイテム"),
        ("examine yard", "庭を調べる"),
        ("cats", "猫を見る"),
        ("place toy", "おもちゃを置く"),
        ("place food", "エサを置く"),
        ("leave yard", "庭を出る"),
    ]
    
    while data["in_yard"]:
        choice = get_choice(actions, "どうしますか?", data["prefix"])
        
        if choice is None:
            continue
        elif choice == "leave yard":
            exit(data)
        elif choice == "list owned items":
            list_owned_items(data)
        elif choice == "examine yard":
            list_yard_items(data)
        elif choice == "cats":
            cats(data)
        elif choice == "place toy":
            place(data)
        elif choice == "place food":
            food(data)


def compute_space(data):
    """Compute available yard space."""
    return data["space"] - sum([item["size"] for item in data["yard"]])


def exit(data):
    """Cancel item placement."""
    data["in_yard"] = False


def list_owned_items(data):
    """Display a list of owned items."""
    owned_items = [item["name"] for item in data["items"].values() if "owned" in item["attributes"]]
    if len(owned_items) == 0:
        printer.warn(data["prefix"], "アイテムを持っていません。ショップで買ってきましょう!")
    else:
        printer.yard(data["prefix"], "持っているアイテム: {0}".format("、".join(owned_items)))


def list_yard_items(data):
    """Display list of items placed in yard."""
    if len(data["yard"]) > 0:
        items = [item for item in data["yard"]]
        for item in items:
            if item["occupied"]:
                printer.yard(data["prefix"], "庭に{0}があります。使っているのは{1}です".format(
                    item["name"], "、".join(item["occupant"])))
            else:
                printer.yard(data["prefix"], "庭に{0}があります。今はだれも使っていません".format(item["name"]))
        cat_activities(data)
    else:
        printer.warn(data["prefix"], "庭には何もありません。さみしいですね")
    check_food(data)


def cat_activities(data):
    """Display cat activities."""
    yard_items = [(obj, obj["occupant"]) for obj in data["yard"] if obj["occupied"]]
    for item in yard_items:
        cats = item[1]
        for cat in cats:
            printer.yard(data["prefix"], "{0}が{1}で遊んでいます".format(cat, item[0]['name']))


def cats(data):
    """Allow you to look at the cats in your yard"""
    cats_in_yard = []
    [cats_in_yard.extend(obj["occupant"]) for obj in data["yard"] if obj["occupied"]]
    
    if len(cats_in_yard) == 0:
        printer.warn(data["prefix"], "今、庭に猫はいません!")
        return
    
    cat_options = [(cat, cat) for cat in cats_in_yard]
    choice = get_choice(cat_options, "どの猫を見ますか?", data["prefix"])
    
    if choice:
        desc_cat(data, choice)

def desc_cat(data, cat):
    printer.yard(data["prefix"], data["cats"][cat]["desc"])


def place(data):
    """Place item in yard."""
    items_list = [item for item in data["items"].values()
                  if "owned" in item["attributes"] and not item["in_yard"]]
    
    placable_items = []
    for item in items_list:
        if item["size"] < 15:
            placable_items.append((item["name"], item["name"]))
    
    if len(placable_items) == 0:
        printer.warn(data["prefix"], "置けるアイテムがありません!")
        return
    
    choice = get_choice(placable_items, "どのアイテムを置きますか?", data["prefix"])
    
    if choice:
        item = next(item for item in items_list if item["name"] == choice)
        try_to_place(data, item)


def try_to_place(data, item):
    """Attempt item placement in yard."""
    if sum([toy["size"] for toy in data["yard"]]) + item["size"] < data["space"]:
        data["yard"].append(item)
        item["in_yard"] = True
        printer.success(data["prefix"], "いいね! 庭には今、{0}があります".format("、".join([toy["name"] for toy in data["yard"]])))
    else:
        printer.warn(data["prefix"], "おっと、庭に入りきりません! どれかと入れ替えますか?")
        offer_replace(data, item)


def offer_replace(data, item):
    """Replace an existing item in yard."""
    yard_items = [(toy["name"], toy["name"]) for toy in data["yard"]]
    
    choice = get_choice(yard_items, "どのアイテムと入れ替えますか?", data["prefix"])
    
    if choice:
        remove_from_yard(data, choice)
        try_to_place(data, item)


def remove_from_yard(data, item_name):
    """Remove item from yard."""
    to_remove = [item for item in data["yard"] if item["name"] == item_name]
    for item in to_remove:
        data["yard"].remove(item)
        # items側も同期（二重保険）
        for master_item in data["items"].values():
            if master_item.get("name") == item_name:
                master_item["in_yard"] = False

def check_food(data):
    """Check food in yard."""
    if data["food_remaining"] == 0:
        printer.warn(data["prefix"], "庭にエサがありません! エサがないと猫は来ませんよ!")
    else:
        printer.success(data["prefix"], "庭に{0}があります(残り{1}分)".format(data["food"], data["food_remaining"]))


def food(data):
    """Display food placement options."""
    check_food(data)
    
    # 所有餌を集計（重複も個別に表示）
    placable_items = []
    for idx, item in enumerate(data["owned_food"]):
        # keyにインデックスも含めて一意にする
        placable_items.append((str(idx), "{0} ({1})".format(item["name"], idx)))
    
    if len(placable_items) == 0:
        printer.warn(data["prefix"], "エサを持っていません! 先にショップで買いましょう!")
        return
    
    choice = get_choice(placable_items, "どれを置きますか?(番号を入力、ENTERでキャンセル)", data["prefix"])
    
    if choice:
        idx = int(choice)
        put_food_in_yard(data, idx)


def put_food_in_yard(data, arr_idx):
    """Place food in yard."""
    food = data["owned_food"].pop(arr_idx)
    data["food"] = food["name"]
    data["food_remaining"] = food["size"]
    printer.success(data["prefix"], "やった! 庭に{0}を置きました(残り{1}分)".format(data["food"], data["food_remaining"]))
