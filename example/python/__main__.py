"""
実際のプロジェクトでの python の応用の一例


このスクリプトは、プロジェクトのルートディレクトリで
`
python3 python
`
とすることで __main__.py が実行できる。
"""

import glob
import sys
from subprocess import run

sys.path.append("./build")

# ---- Pre script -----
# tmux を使っている場合は tmux のコマンドで新しく pane を作ったりできる。
run(["tmux", "split-window", "-t", "0", "-b"])
run(["tmux", "select-pane", "-t", "1"])

# 複数 pane がある時は以下のようにして pane のindex と tty の対応を取ることができる。
panes: str = run(
    ["tmux", "list-panes", "-F", "#{pane_index} #{pane_tty}"],
    capture_output=True,
    text=True,
).stdout
panes_dict = {
    i[0]: i[1] for i in [pane.split(" ") for pane in panes.split("\n") if pane != ""]
}

# 以下で ipython を立てた時にあらかじめ実行したいコマンドを書いておく
pre_script = f"""
import sys

sys.path.append("./build")

import python
import pyshell

def start():
    pyshell.start("", tty="{panes_dict["1"]}") # のようにして使う
"""

run(["ipython3", "-i", "-c", pre_script])

# ---- Post script -----
run(["tmux", "kill-pane", "-t", "0"])
