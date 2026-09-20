"""
Print output.

This module handles special printing of output to player including
colorization of game areas.
"""

# 画面ごとの見出し。表示にも色分けの判定にも使うので、ここで一元管理する。
PREFIX_MAIN = "[メインメニュー]"
PREFIX_WELCOME = "[ようこそ!]"
PREFIX_SHOP = "[ショップ]"
PREFIX_YARD = "[おにわ]"

# 通貨の表示名(内部キーは "s" / "g" のまま)。にぼし・かつおぶし等に変えたい場合はここだけ直す。
CURRENCY_NAME = {"s": "銀", "g": "金"}


class PColors:
    """Define some colors up in this piece."""

    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    GOODBYE = '\033[93m'
    HELP = '\033[36m'
    MAIN = '\033[37m'
    SHOP = '\033[95m'
    YARD = '\033[32m'
    TREASURE = '\033[35m'
    ENDC = '\033[0m'

    def disable(self):
        """Disable colorization and revert to plain text."""
        self.RED = ''
        self.YELLOW = ''
        self.GREEN = ''
        self.BLUE = ''
        self.PURPLE = ''
        self.GOODBYE = ''
        self.HELP = ''
        self.MAIN = ''
        self.SHOP = ''
        self.YARD = ''
        self.ENDC = ''


def price(amount, currency):
    """値段の短い表記。例: 銀5 / 金15"""
    return "{0}{1}".format(CURRENCY_NAME[currency], amount)


def fish_text(amount, currency):
    """さかなの数の表記。例: 銀のさかな12匹"""
    return "{0}のさかな{1}匹".format(CURRENCY_NAME[currency], amount)


def _prefix_color(prefix):
    if prefix == PREFIX_SHOP:
        return PColors.SHOP
    if prefix == PREFIX_YARD:
        return PColors.YARD
    return PColors.MAIN


def _out(prefix, words, words_color=""):
    """見出し(画面ごとの色)+本文(必要なら色付き)を1行で出力する。"""
    end = PColors.ENDC if words_color else ""
    print("{0}{1}{2} {3}{4}{5}".format(
        _prefix_color(prefix), prefix, PColors.ENDC,
        words_color, words, end))


def invalid(prefix):
    """Apologize for not understand user input"""
    _out(prefix, "すみません、よくわかりませんでした。", PColors.YELLOW)


def fail(prefix, words):
    """Print failure messages."""
    if prefix in (PREFIX_SHOP, PREFIX_YARD):
        _out(prefix, words, PColors.RED)
    else:
        _out(prefix, words, PColors.YELLOW)


def prompt(prefix, actions):
    """Action prompt."""
    _out(prefix, "選べる行動:")
    for i, action in enumerate(actions, 1):
        print("  {0}. {1}".format(i, action))


def p(prefix, words):
    """Print plain messages."""
    print("{} {}".format(prefix, words))


def shop(prefix, words):
    """Print shop messages."""
    print("{0}{1}{2} {3}".format(PColors.SHOP, prefix, PColors.ENDC, words))


def success(prefix, words):
    """Print success messages."""
    _out(prefix, words, PColors.GREEN)


def warn(prefix, words):
    """Print warning messages."""
    _out(prefix, words, PColors.YELLOW)


def yard(prefix, words):
    """Print yard messages."""
    print("{0}{1}{2} {3}".format(PColors.GREEN, prefix, PColors.ENDC, words))
