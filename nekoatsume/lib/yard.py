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
        printer.warn(prefix, "No options available!")
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
    
    # 文字入力（大文字小文字・冠詞無視でマッチ）
    raw_norm = raw.strip().lower()
    raw_norm = raw_norm.lstrip("a ").lstrip("an ").lstrip("the ")
    
    for key, name in options:
        if raw_norm == key.lower():
            return key
        # 表示名でもマッチ
        name_norm = name.lower().lstrip("a ").lstrip("an ").lstrip("the ")
        if raw_norm == name_norm:
            return key
    
    printer.warn(prefix, "I'm sorry I didn't recognize that option")
    return None


def menu(data):
    """Display yard menu."""
    data["prefix"] = "[The Yard]"
    list_yard_items(data)
    data["in_yard"] = True
    
    actions = [
        ("list owned items", "List owned items"),
        ("examine yard", "Examine yard"),
        ("cats", "Look at cats"),
        ("place toy", "Place toy"),
        ("place food", "Place food"),
        ("leave yard", "Leave yard"),
    ]
    
    while data["in_yard"]:
        choice = get_choice(actions, "What do you want to do?", data["prefix"])
        
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
        printer.warn(data["prefix"], "You don't own any items, better go buy some in the shop~!")
    else:
        printer.yard(data["prefix"], "You currently own a {0}".format(", and a ".join(owned_items)))


def list_yard_items(data):
    """Display list of items placed in yard."""
    if len(data["yard"]) > 0:
        items = [item for item in data["yard"]]
        for item in items:
            cats = "no one"
            if item["occupied"]:
                cats = ", and ".join([cat for cat in item["occupant"]])
            printer.yard(data["prefix"], "Your yard currently has a {0} in it, occupied by {1}".format(item["name"], cats))
        cat_activities(data)
    else:
        printer.warn(data["prefix"], "You currently have nothing in your yard, how sad")
    check_food(data)


def cat_activities(data):
    """Display cat activities."""
    yard_items = [(obj, obj["occupant"]) for obj in data["yard"] if obj["occupied"]]
    for item in yard_items:
        cats = item[1]
        for cat in cats:
            printer.yard(data["prefix"], "{0} is playing with a {1}".format(cat, item[0]['name']))


def cats(data):
    """Allow you to look at the cats in your yard"""
    cats_in_yard = []
    [cats_in_yard.extend(obj["occupant"]) for obj in data["yard"] if obj["occupied"]]
    
    if len(cats_in_yard) == 0:
        printer.warn(data["prefix"], "There are no cats in your yard right now!")
        return
    
    cat_options = [(cat, cat) for cat in cats_in_yard]
    choice = get_choice(cat_options, "Which cat would you like to look at?", data["prefix"])
    
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
        printer.warn(data["prefix"], "You don't have any items to place!")
        return
    
    choice = get_choice(placable_items, "Which item would you like to place?", data["prefix"])
    
    if choice:
        item = next(item for item in items_list if item["name"] == choice)
        try_to_place(data, item)


def try_to_place(data, item):
    """Attempt item placement in yard."""
    if sum([toy["size"] for toy in data["yard"]]) + item["size"] < data["space"]:
        data["yard"].append(item)
        item["in_yard"] = True
        printer.success(data["prefix"], "Nice! Your yard now consists of a {0}".format(", and a ".join([toy["name"] for toy in data["yard"]])))
    else:
        printer.warn(data["prefix"], "Oops that won't fit in your yard! Would you like to replace an item?")
        offer_replace(data, item)


def offer_replace(data, item):
    """Replace an existing item in yard."""
    yard_items = [(toy["name"], toy["name"]) for toy in data["yard"]]
    
    choice = get_choice(yard_items, "Which item would you like to replace?", data["prefix"])
    
    if choice:
        remove_from_yard(data, choice)
        try_to_place(data, item)


def remove_from_yard(data, item_name):
    """Remove item from yard."""
    to_remove = [item for item in data["yard"] if item["name"] == item_name]
    for item in to_remove:
        data["yard"].remove(item)
        item["in_yard"] = False


def check_food(data):
    """Check food in yard."""
    if data["food_remaining"] == 0:
        printer.warn(data["prefix"], "Your yard currently doesn't have any food in it! No cats will come if there's no food!")
    else:
        printer.success(data["prefix"], "Your yard currently has a {0} in it with {1} time remaining".format(data["food"], data["food_remaining"]))


def food(data):
    """Display food placement options."""
    check_food(data)
    
    # 所有餌を集計（重複も個別に表示）
    placable_items = []
    for idx, item in enumerate(data["owned_food"]):
        # keyにインデックスも含めて一意にする
        placable_items.append((str(idx), "{0} ({1})".format(item["name"], idx)))
    
    if len(placable_items) == 0:
        printer.warn(data["prefix"], "You don't have any food! Buy some in the shop first!")
        return
    
    choice = get_choice(placable_items, "Which would you like to place? (number or ENTER to cancel)", data["prefix"])
    
    if choice:
        idx = int(choice)
        put_food_in_yard(data, idx)


def put_food_in_yard(data, arr_idx):
    """Place food in yard."""
    food = data["owned_food"].pop(arr_idx)
    data["food"] = food["name"]
    data["food_remaining"] = food["size"]
    printer.success(data["prefix"], "Sweet! Your yard now has a {0} set out, and {1} of food remaining".format(data["food"], data["food_remaining"]))
