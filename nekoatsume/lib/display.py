"""
Display of information to player.

These are the functions which show the player what is happening in the game.
"""

from __future__ import print_function
from lib import buy_menu
from lib import data_constructor
import datetime
import json
import os
import sys
from lib import yard
from lib import printer
import time
from lib import update
import readline
import random

try:
    input = raw_input
except NameError:
    pass


# ========== タイプライター表示関数 ==========
def tw(text, delay=0.03):
    """タイプライター風に一文字ずつ表示する"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # 最後に改行


def store_data(data):
    """Purrsist the data."""
    data_file = os.getcwd() + '/var/data.json'
    if data.get("completer"):
        del data["completer"]
    
    # ========== 追加：yardとitemsの整合性を同期 ==========
    # yardにあるアイテム名を集める
    yard_item_names = set()
    for item in data.get("yard", []):
        if isinstance(item, dict):
            yard_item_names.add(item.get("name", ""))
    
    # items側のin_yardをyardの実態に合わせる
    for item in data.get("items", {}).values():
        if isinstance(item, dict):
            item["in_yard"] = item.get("name", "") in yard_item_names
    
    with open(data_file, 'w') as f:
        json.dump(data, f)

def load_data():
    """Load the data."""
    data_file = os.getcwd() + '/var/data.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    return data


def prep_data_on_close(data):
    """Prepare data for game exit."""
    store_data(data)


def banner():
    """Welcome banner."""
    banner_file = os.getcwd() + '/share/banner.dat'
    with open(banner_file, 'r') as b:
        for l in b:
            print(l.format(printer.PColors, printer.PColors), end='')
        print('\n')


def compute_interactions(data):
    """Compute cat interactions."""
    cur_time = datetime.datetime.now()
    time_since = (cur_time - data["start"]).total_seconds()
    if time_since < data["food_remaining"]:
        data["food_remaining"] -= time_since
        return compute_with_food(time_since)
    else:
        time_w_food = data["food_remaining"]
        time_wo_food = time_since - time_w_food
        data["food_remaining"] = 0
        return compute_with_food(time_w_food)
    return compute


def desc_yard(data):
    """Describe current yard situation."""
    toys = [item for item in data["yard"]]
    tw("庭は全部で{0}マスあります".format(6))
    for toy in toys:
        if toy["occupant"]:
            tw("{0}は{1}が使っています".format(
                toy["name"], "、".join(toy["occupant"])))
        else:
            tw("{0}は空いています".format(toy["name"]))


def check_status(data):
    """Check status of items in yard."""
    yard.list_yard_items(data)


def bestow_treasures(data, prev_start):
    """Randomly decide whether or not to give the user a treasure."""
    if not prev_start:
        return
    if not data.get("cats"):
        return
    not_given = [cat for cat in data["cats"].values()
                   if isinstance(cat, dict)
                   and cat.get("total_time_in_yard", 0) > 0
                   and not cat.get("given_treasure", False)]
    if not not_given:
        return
    since_last_run = data["start"] - prev_start
    if since_last_run < 0:
        since_last_run = 0
    absent = since_last_run / datetime.timedelta(days=7).total_seconds()
    bonus = min(1.0, absent)
    base = 0.05
    prob = base + (base*bonus)
    rnd = random.random()
    if rnd >= prob:
        return
    if not not_given:
        return
    giver = random.choice(not_given)
    data["cats"][giver["name"]]["given_treasure"] = True
    data["pending_treasures"].append([giver["name"], giver["treasure"]])


def recieve_treasures(data):
    if len(data["pending_treasures"]) == 0:
        return
    for treasure in data["pending_treasures"]:
        if isinstance(treasure, (list, tuple)) and len(treasure) >= 2:
            tw("{0}がお宝をくれました!「{1}」!!!".format(treasure[0], treasure[1]))
    data["pending_treasures"] = []


def check_treasures(data):
    treasures = [cat for cat in data["cats"].values() if cat.get("given_treasure", False)]
    if treasures:
        for cat in treasures:
            tw("{0}からもらったお宝:「{1}」!".format(
                cat["name"], cat["treasure"]))
    else:
        tw("まだ猫からお宝をもらっていません…。でも大丈夫! 続けていれば、きっともらえますよ!")


def collect_money(data):
    """Collect money left by cats."""
    if len(data["pending_money"]) == 0:
        tw("猫たちはまだ何も残していきませんでした")
        return
    pending = data["pending_money"][:]
    data["pending_money"] = []
    for money in pending:
        if isinstance(money, (list, tuple)) and len(money) >= 3:
            currency = money[2]
            tw("やったね! {0}が{1}を置いていきました!".format(
                money[0], printer.fish_text(money[1], currency)))
            data[currency + "_fish"] += money[1]


def print_help(data):
    """Print the game help."""
    tw("ネコあつめへようこそ!")
    tw("このゲームでは、猫たちがあなたの庭に遊びに来て、あなたはごはんをあげます。")
    tw("とてもいいゲームなので、ぜひもっと遊んでね。")
    tw("メニューは、番号かコマンド名を入力して選べます。")


def quit(data):
    """Quit the game."""
    data["want_to_play"] = False
    tw("ゲームを保存しました。またね!")
    prep_data_on_close(data)


class actionCompleter(object):

    def __init__(self):
        return

    def set_actions(self, actions):
        self.actions = sorted(actions)

    def complete(self, action, index):
        buf = readline.get_line_buffer()
        if index == 0:
            if buf != "":
                self.matches = [a for a in self.actions if a.startswith(buf)]
            else:
                self.matches = self.actions[:]
        response = self.matches[index]
        if response:
            if action != buf:
                response = response[len(buf)-len(action):]
            return response


def main(data):
    """Main game function."""
    data["want_to_play"] = True
    prev_start = data.get("start", None)
    data["start"] = time.time()
    actions = {"庭を見る": check_status,
               "庭に出る": yard.menu,
               "ショップ": buy_menu.menu,
               "さかなを受け取る": collect_money,
               "エサを確認": yard.check_food,
               "お宝を確認": check_treasures,
               "ヘルプ": print_help,
               "終了": quit}
    labels = list(actions.keys())
    banner()
    data["prefix"] = "{.BLUE}" + printer.PREFIX_WELCOME + "{.ENDC}"
    data["prefix"] = data["prefix"].format(printer.PColors, printer.PColors)
    check_status(data)
    bestow_treasures(data, prev_start)
    recieve_treasures(data)
    data["prefix"] = printer.PREFIX_MAIN
    data["completer"] = actionCompleter()

    readline.set_completer(data["completer"].complete)
    readline.parse_and_bind('tab: complete')
    while data["want_to_play"] is True:
        data["completer"].set_actions(labels)
        data["prefix"] = printer.PREFIX_MAIN
        printer.prompt(data["prefix"], labels)
        inp = input("{0} 行動を選んでください! ".format(data["prefix"])).strip()
        try:
            # 番号入力(全角数字もOK)
            idx = int(inp)
            if 1 <= idx <= len(labels):
                inp = labels[idx - 1]
        except ValueError:
            pass
        if inp in actions:
            actions[inp](data)
            continue
        else:
            printer.invalid(data["prefix"])


def run():
    try:
        data = []
        try:
            data = load_data()
            data = update.update(data)
        except IOError:
            data_constructor.build_data()
            data = load_data()
        main(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)
    finally:
        prep_data_on_close(data)
