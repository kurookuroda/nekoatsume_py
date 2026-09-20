"""
Buy some items.

This module controls the item shop and related transactions.
"""

from lib import printer
DEMARCATION = 15

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

    for i, (key, name) in enumerate(options, 1):
        printer.shop(prefix, "{0}. {1}".format(i, name))
    
    raw = input("{.SHOP}{}{.ENDC} {} ".format(
        printer.PColors, prefix, printer.PColors, prompt))
    
    if raw.strip() == "":
        return None
    
    try:
        idx = int(raw.strip())
        if 1 <= idx <= len(options):
            return options[idx - 1][0]
    except ValueError:
        pass
    
    raw_norm = raw.strip().lower()
    
    for key, name in options:
        if raw_norm == key.lower() or raw_norm == name.lower():
            return key
    
    printer.warn(prefix, "その選択肢はわかりませんでした")
    return None


def menu(data):
    """Display item shop menu."""
    data["prefix"] = printer.PREFIX_SHOP
    printer.shop(
        data["prefix"], "所持金: {0}、{1}"
        .format(printer.fish_text(data["s_fish"], "s"),
                printer.fish_text(data["g_fish"], "g")))
    list_items(data)
    data["want_to_buy"] = True
    
    actions = [
        ("buy", "買う"),
        ("examine", "調べる"),
        ("check wallet", "財布を見る"),
        ("list items", "商品一覧"),
        ("leave shop", "ショップを出る"),
    ]
    
    while data["want_to_buy"]:
        choice = get_choice(actions, "どうしますか?", data["prefix"])
        
        if choice is None:
            continue
        elif choice == "leave shop":
            exit_buy(data)
        elif choice == "buy":
            buy_item(data)
        elif choice == "examine":
            ex_item(data)
        elif choice == "check wallet":
            wallet(data)
        elif choice == "list items":
            list_items(data)


def list_items(data):
    """Display list of available items."""
    catalog = [item for item in data["items"].values()
               if item["attributes"] == [] and item["size"] < DEMARCATION]
    food = [item for item in data["items"].values()
            if item["attributes"] == [] and item["size"] > DEMARCATION]
    owned = [item for item in data["items"].values()
             if "owned" in item["attributes"]]
    for item in catalog:
        printer.shop(
            data["prefix"], "{0} {1}: {2}".format(
                "(おもちゃ)", item["name"], printer.price(item["cost"], item["currency"])))
    for item in food:
        printer.shop(
            data["prefix"], "{0} {1}: {2}".format(
                "(エサ)", item["name"], printer.price(item["cost"], item["currency"])))
    if len(owned) > 0:
        printer.shop(
            data["prefix"], "持っているおもちゃ: {0}".format(
                "、".join([item["name"] for item in owned])))


def exit_buy(data):
    """Cancel purchase."""
    data["want_to_buy"] = False


def wallet(data):
    """Show wallet contents."""
    printer.shop(
        data["prefix"], "所持金: {0}、{1}"
        .format(printer.fish_text(data["s_fish"], "s"),
                printer.fish_text(data["g_fish"], "g")))


def ex_item(data):
    """Examine item."""
    items = []
    for key, item in data["items"].items():
        display = "{0} ({1})".format(item["name"], printer.price(item["cost"], item["currency"]))
        items.append((key, display))
    
    choice = get_choice(items, "どれを調べますか?", data["prefix"])
    
    if choice:
        item = data["items"][choice]
        printer.shop(data["prefix"], item.get("description", "説明はありません。"))


def buy_item(data):
    """Buy an item."""
    buyable_items = []
    for key, item in data["items"].items():
        if item["attributes"] == []:
            display = "{0} ({1})".format(item["name"], printer.price(item["cost"], item["currency"]))
            buyable_items.append((key, display))
    
    if len(buyable_items) == 0:
        printer.warn(data["prefix"], "買えるものがありません!")
        return
    
    choice = get_choice(buyable_items, "何を買いますか?", data["prefix"])
    
    if choice:
        try_to_buy(data, choice)

def try_to_buy(data, item_name):
    """Attempt to buy an item."""
    item = data["items"][item_name]
    currency = item["currency"] + "_fish"
    money = data[currency]
    cost = item["cost"]
    if money < cost:
        printer.fail(
            data["prefix"], "ごめんなさい、お金が足りません!")
        return
    else:
        data[currency] = data[currency] - cost
        if item["size"] < 6:
            data["items"][item_name]["attributes"] = ["owned"]
        else:
            data["owned_food"].append(item.copy())
        printer.success(data["prefix"], "まいど! すばらしい選択です!")
        return
