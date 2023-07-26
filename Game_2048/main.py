"""2048游戏
本模块已完整实现2048游戏的算法及分数的计算算法
本游戏的界面采用python 标准库 tkinter 来实现
此界面的布局采用tkinter中的grid布局
"""

import copy
import random  # 导入随机模块random,主要用于随机生成新的数字及数字摆方位置
import math  # 导入数学模块,用来计算分数
import conn_db as db  # 导入数据连接模块
from tkinter import *
from tkinter import messagebox
from tkinter.colorchooser import askcolor
from tkinter.simpledialog import askinteger, askfloat, askstring
from tkinter.messagebox import showinfo, showwarning, showerror

# _map_data 绑定一个 4 x 4 列表,此列表为2048游戏地图，初始值如下:


_map_data = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

# score_list = [random.randrange(100, 1000) for i in range(0, 10)]  # 分数列表
# score_list = db.get_data()
score_list = []
for i in range(len(db.get_data())):
    score_list.append(db.get_data()[i]['分数'])


# -------------------------以下为2048游戏的基本算法---------------------------


def reset():
    """重新设置游戏数据,将地图恢复为初始状态，并加入两个数据 2 作用初始状态"""
    _map_data[:] = []  # _map_data.clear()
    _map_data.append([0, 0, 0, 0])
    _map_data.append([0, 0, 0, 0])
    _map_data.append([0, 0, 0, 0])
    _map_data.append([0, 0, 0, 0])
    # 在空白地图上填充两个2
    fill2()
    fill2()


def get_space_count():
    """获取没有数字的方格的数量,如果数量为0则说有无法填充新数据，游戏即将结束
    """
    count = 0
    for r in _map_data:
        count += r.count(0)
    return count


def get_score():
    """获取游戏的分数,得分规则是每次有两个数加在一起则生成相应的分数。
    如 2 和 2 合并后得4分, 8 和 8 分并后得 16分.
    根据一个大于2的数字就可以知道他共合并了多少次，可以直接算出分数:
    如:
       4 一定由两个2合并，得4分
       8 一定由两个4合并,则计:8 + 4 + 4 得32分
       ... 以此类推
    """
    score = 0
    for r in _map_data:
        for c in r:
            score += 0 if c < 4 else c * int((math.log(c, 2) - 1.0))
    return score  # 导入数学模块


def fill2():
    """填充2到空位置，如果填度成功返回True,如果已满，则返回False"""
    blank_count = get_space_count()  # 得到地图上空白位置的个数
    if 0 == blank_count:
        return False
    # 生成随机位置, 如，当只有四个空时，则生成0~3的数，代表自左至右，自上而下的空位置
    pos = random.randrange(0, blank_count)
    offset = 0
    for row in _map_data:  # row为行row
        for col in range(4):  # col 为列，column
            if 0 == row[col]:
                if offset == pos:
                    # 把2填充到第row行，第col列的位置，返回True
                    row[col] = 2
                    return True
                offset += 1


def is_gameover():
    """判断游戏是否结束,如果结束返回True,否是返回False
    """
    for r in _map_data:
        # 如果水平方向还有0,则游戏没有结束
        if r.count(0):
            return False
        # 水平方向如果有两个相邻的元素相同，应当是可以合并的，则游戏没有结束
        for i in range(3):
            if r[i] == r[i + 1]:
                return False
    for c in range(4):
        # 竖直方向如果有两个相邻的元素相同，应当可以合并的，则游戏没有结束
        for r in range(3):
            if _map_data[r][c] == _map_data[r + 1][c]:
                return False

    # 以上都没有，则游戏结束
    return True


# 以下是2048游戏的基本算法,此算法是在达内的美女老师"贾琳倩"提供算法上改进而来
# 此种算法不是最优算法,但我认为这是目前最容易理解的算法


def _left_move_number(line):
    """左移一行数字,如果有数据移动则返回True，否则返回False:
    如: line = [0, 2, 0, 8] 即表达如下一行:
        +---+---+---+---+
        | 0 | 2 | 0 | 8 |      <----向左移动
        +---+---+---+---+
    此行数据需要左移三次:
      第一次左移结果:
        +---+---+---+---+
        | 2 | 0 | 8 | 0 |
        +---+---+---+---+
      第二次左移结果:
        +---+---+---+---+
        | 2 | 8 | 0 | 0 |
        +---+---+---+---+
      第三次左移结果:
        +---+---+---+---+
        | 2 | 8 | 0 | 0 |  # 因为最左则为2,所以8不动
        +---+---+---+---+
     最终结果: line = [4, 8, 0, 0]
    """
    moveflag = False  # 是否移动的标识,先假设没有移动
    for _ in range(3):  # 重复执行下面算法三次
        for i in range(3):  # i为索引
            if 0 == line[i]:  # 此处有空位，右侧相邻数字向左侧移动，右侧填空白
                moveflag = True
                line[i] = line[i + 1]
                line[i + 1] = 0
    return moveflag


def _left_marge_number(line):
    """向左侧进行相同单元格合并,合并结果放在左侧,右侧补零
    如: line = [2, 2, 4, 4] 即表达如下一行:
        +---+---+---+---+
        | 2 | 2 | 4 | 4 |
        +---+---+---+---+
    全并后的结果为:
        +---+---+---+---+
        | 4 | 0 | 8 | 0 |
        +---+---+---+---+
    最终结果: line = [4, 8, 8, 0]
    """
    moveflag = False
    for i in range(3):
        if line[i] == line[i + 1]:
            moveflag = True
            line[i] *= 2  # 左侧翻倍
            line[i + 1] = 0  # 右侧归零
    return moveflag


def _left_move_aline(line):
    """左移一行数据,如果有数据移动则返回True，否则返回False:
    如: line = [2, 0, 2, 8] 即表达如下一行:
        +---+---+---+---+
        | 2 |   | 2 | 8 |      <----向左移动
        +---+---+---+---+
    左移算法分为三步:
        1. 将所有数字向左移动来填补左侧空格,即:
            +---+---+---+---+
            | 2 | 2 | 8 |   |
            +---+---+---+---+
        2. 判断是否发生碰幢，如果两个相临且相等的数值则说明有碰撞需要合并,
           合并结果靠左，右则填充空格
            +---+---+---+---+
            | 4 |   | 8 |   |
            +---+---+---+---+
        3. 再重复第一步，将所有数字向左移动来填补左侧空格,即:
            +---+---+---+---+
            | 4 | 8 |   |   |
            +---+---+---+---+
        最终结果: line = [4, 8, 0, 0]
    """
    moveflag = False
    if _left_move_number(line):
        moveflag = True
    if _left_marge_number(line):
        moveflag = True
    if _left_move_number(line):
        moveflag = True
    return moveflag


def left():
    """游戏左键按下时或向左滑动屏幕时的算法"""
    moveflag = False  # moveflag 是否成功移动数字标志位,如果有移动则为真值,原地图不变则为假值

    # 将第一行都向左移动.如果有移动就返回True
    for line in _map_data:
        if _left_move_aline(line):
            moveflag = True
    return moveflag


def right():
    """游戏右键按下时或向右滑动屏幕时的算法
    选将屏幕进行左右对调，对调后，原来的向右滑动即为现在的向左滑动
    滑动完毕后，再次左右对调回来
    """
    # 左右对调
    for r in _map_data:
        r.reverse()
    moveflag = left()  # 向左滑动
    # 再次左右对调
    for r in _map_data:
        r.reverse()
    return moveflag


def up():
    """游戏上键按下时或向上滑动屏幕时的算法
    先把每一列都自上而下放入一个列表中line中，然后执行向滑动，
    滑动完成后再将新位置摆回到原来的一列中
    """
    moveflag = False
    line = [0, 0, 0, 0]  # 先初始化一行，准备放入数据
    for col in range(4):  # 先取出每一列
        # 把一列中的每一行数入放入到line中
        for row in range(4):
            line[row] = _map_data[row][col]
        # 将当前列进行上移，即line 左移
        if _left_move_aline(line):
            moveflag = True
        # 把左移后的 line中的数据填充回原来的一列
        for row in range(4):
            _map_data[row][col] = line[row]
    return moveflag


def down():
    """游戏下键按下时或向下滑动屏幕时的算法
    选将屏幕进行上下对调，对调后，原来的向下滑动即为现在的向上滑动
    滑动完毕后，再次上下对调回来
    """
    _map_data.reverse()
    moveflag = up()  # 上滑
    _map_data.reverse()
    return moveflag


# 音乐播放
def music_play():
    import pygame as py
    # 初始化
    py.mixer.init()
    # 文件加载
    py.mixer.music.load(r'.\test.mp3')
    # 播放  第一个是播放值 -1代表循环播放， 第二个参数代表开始播放的时间
    py.mixer.music.play(-1, 10)


# -------------------------以下为2048游戏的操作界面---------------------------


def set_score(player, score):
    db.set_data(player=player, score=score)


def record_score(score):
    _grade_list = copy.copy(score_list)
    _grade_list.append(score)
    grade_list = list(set(_grade_list))
    grade_list.sort(reverse=True)
    for i in range(len(grade_list)):
        # 对比取出数据与待查找数据
        if grade_list[i] == score:
            # 查找成功,返回当前下标值
            return i + 1
        # 查找完所有数据，仍未找到
    # 查找失败，返回非法下标值
    return -1


def on_key_down(event):
    """键盘按下处理函数"""
    keysym = event.keysym
    if keysym in keymap:
        if keymap[keysym]():  # 如果有数字移动
            fill2()  # 填充一个新的2
    update_ui()
    if is_gameover():
        inputB = Entry(root)
        inputB.grid(row=5, column=3, padx=5, pady=5)
        set_score(get_player(), get_score())
        mb = messagebox.askyesno(
            title="gameOver", message="游戏结束!\n是否退出游戏!")
        if mb:
            root.quit()
        else:
            reset()
            update_ui()


def update_ui():
    """刷新界面函数
    根据计算出的f地图数据,更新各个Label的设置
    """
    for r in range(4):
        for c in range(len(_map_data[0])):
            number = _map_data[r][c]  # 设置数字
            label = map_labels[r][c]  # 选中Lable控件
            label['text'] = str(number) if number else ''
            label['bg'] = mapcolor[number][0]
            label['foreground'] = mapcolor[number][1]
    label_score['text'] = str(get_score())  # 重设置分数
    label_ranking['text'] = str(record_score(get_score()))  # 重设置排名


# 以下排名按钮
# def history_game():
#     history_list = list(set(score_list))
#     history_list.sort(reverse=True)
#     message_data = ""
#     for i in range(len(history_list)):
#         message_data += f"第{i + 1}名:分数为{history_list[i]}\n"
#     if not message_data:
#         message_data = "暂无排名"
#     messagebox.showwarning(title='历史排名', message=message_data)
# 排名
def history_game():
    history_list = db.get_data()
    message_data = ""
    for i in range(len(history_list)):
        message_data += f"NO.{i + 1:<2} 分数为:{history_list[i]['分数']:<7d}\n玩家:{history_list[i]['玩家']:<} 时间:{history_list[i]['创建时间']}\n"
    if not message_data:
        message_data = "暂无排名"
    messagebox.showwarning(title='前10排名', message=message_data)


# 以下设置重新开始按钮
def reset_game():
    # 这个会导致重新插入数据
    # set_score(get_score())
    reset()
    update_ui()
    label_ranking['text'] = '0'  # 重设置排名


def game_parameters():
    messagebox.showwarning(title="警告", message="还在调试......\n点你妹")
    return False
    # isParams = messagebox.askyesno(title="设置参数", message="是否进行设置游戏参数")
    # if isParams:
    #     # 设置背景颜色
    #     def chooseColor(detail_color, title):
    #         color = askcolor(color=detail_color, title=title)
    #         return color[1]
    #
    #     game_bg_color = chooseColor("#bbada0", '选择背景色')
    #     if not game_bg_color:
    #         "#bbada0"
    #
    #     block_color = chooseColor("#cdc1b4", '选择方块色')
    #     if not block_color:
    #         block_color = "#cdc1b4"
    #
    #     mapcolor[0] = (block_color, block_color)
    # else:
    #     messagebox.showwarning(title='start', message="开始游戏")


# 获取输入框内容
def get_player():
    player_value = player.get()
    while True:
        if not player_value:
            messagebox.showerror(title='提示', message='请TM先输入你丫的大名，会不会！！！')
            return True
        else:
            # 禁用输入框
            player.config(state='readonly')
            # 禁用提交按钮
            player_button.config(state='disabled')
            # 面板获得焦点
            frame.focus_set()
            # 绑定
            frame.bind("<Key>", on_key_down)
            break
    return player_value


if __name__ == '__main__':

    # 初始化音乐
    # music_play()

    # 先重新设置游戏数据
    reset()
    # 创建tkinter窗口
    root = Tk()
    # 设置标题文字
    root.title('Game_2048')
    # 获得屏幕宽度
    screen_width = root.winfo_screenwidth()
    # 获得屏幕高度
    screen_height = root.winfo_screenheight()
    # （x轴长，y轴长，x坐标，y坐标）
    root.geometry('%dx%d+%d+%d' % (484, 525, (screen_width - 500) / 2, (screen_height - 550) / 2))
    root.resizable(width=False, height=False)  # 固定宽和高

    # 背景色
    game_bg_color = "#bbada0"

    # 设置游戏中每个数据对应色块的颜色
    mapcolor = {
        0: ("#cdc1b4", "#776e65"),
        2: ("#eee4da", "#776e65"),
        4: ("#ede0c8", "#f9f6f2"),
        8: ("#f2b179", "#f9f6f2"),
        16: ("#f59563", "#f9f6f2"),
        32: ("#f67c5f", "#f9f6f2"),
        64: ("#f65e3b", "#f9f6f2"),
        128: ("#edcf72", "#f9f6f2"),
        256: ("#edcc61", "#f9f6f2"),
        512: ("#e4c02a", "#f9f6f2"),
        1024: ("#e2ba13", "#f9f6f2"),
        2048: ("#ecc400", "#f9f6f2"),
        4096: ("#ae84a8", "#f9f6f2"),
        8192: ("#b06ca8", "#f9f6f2"),
        # ----其它颜色都与8192相同---------
        2 ** 14: ("#b06ca8", "#f9f6f2"),
        2 ** 15: ("#b06ca8", "#f9f6f2"),
        2 ** 16: ("#b06ca8", "#f9f6f2"),
        2 ** 17: ("#b06ca8", "#f9f6f2"),
        2 ** 18: ("#b06ca8", "#f9f6f2"),
        2 ** 19: ("#b06ca8", "#f9f6f2"),
        2 ** 20: ("#b06ca8", "#f9f6f2"),
    }

    # 以下是键盘映射
    keymap = {
        'a': left,
        'd': right,
        'w': up,
        's': down,
        'Left': left,
        'Right': right,
        'Up': up,
        'Down': down,
    }

    # 顶部
    head = Frame(root, bg=game_bg_color)
    head.grid(sticky=N + E + W + S)
    # 标签
    player_label = Label(head, text="来将可留姓名: ", font=('微软雅黑', 12, 'bold'), bg=game_bg_color, fg='#ffffff')
    player_label.grid(row=0, padx=0, pady=5, sticky="w")
    # 输入框
    player = Entry(head, border=0, width=35)
    player.grid(row=0, pady=5, column=1)
    player.focus_set()
    # 提交按钮
    player_button = Button(text="提交", width=13, font=('黑体', 12), border=0, bg='#8f7a66', fg='#ffffff',
                           command=get_player)
    player_button.grid(row=0, columnspan=2, padx=5, pady=5, sticky=E)

    # 主要部分
    frame = Frame(root, bg=game_bg_color)

    frame.grid(sticky=N + E + W + S)

    # 初始化图形界面
    # 创建4x4的数字块
    # 游戏各方块的lable Widget
    map_labels = []
    for r in range(4):
        row = []
        for c in range(len(_map_data[0])):
            value = _map_data[r][c]
            text = str(value) if value else ''
            player_label = Label(frame, text=text, width=5, height=2,
                                 font=("黑体", 30, "bold"))
            player_label.grid(row=r, column=c, padx=5, pady=5, sticky=N + E + W + S)
            row.append(player_label)
        map_labels.append(row)

    # 设置显示分数的Lable
    player_label = Label(frame, text='分数', font=("黑体", 30, "bold"),
                         bg="#bbada0", fg="#eee4da")
    player_label.grid(row=4, column=0, padx=5, pady=5)
    # 设置显示分数
    label_score = Label(frame, text='0', font=("黑体", 30, "bold"),
                        bg="#bbada0", fg="#ffffff")
    label_score.grid(row=4, columnspan=1, column=1, padx=5, pady=5)
    # 设置显示排名的Lable
    ranking = Label(frame, text='排名', font=("黑体", 30, "bold"),
                    bg="#bbada0", fg="#eee4da")
    ranking.grid(row=4, column=2, padx=5, pady=5)
    # 设置显示排名
    label_ranking = Label(frame, text='0', font=("黑体", 30, "bold"),
                          bg="#bbada0", fg="#ffffff")
    label_ranking.grid(row=4, columnspan=3, column=3, padx=5, pady=5)

    # 排名记录
    history_button = Button(frame, text='排名记录', font=("黑体", 16, "bold"),
                            bg="#8f7a66", fg="#f9f6f2", command=history_game)
    history_button.grid(row=5, column=0, padx=5, pady=5)

    # 游戏参数
    parameter_button = Button(frame, text='游戏参数', font=("黑体", 16, "bold"),
                              bg="#8f7a66", fg="#f9f6f2", command=game_parameters)
    parameter_button.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

    # 重新开始
    restart_button = Button(frame, text='重新开始', font=("黑体", 16, "bold"),
                            bg="#8f7a66", fg="#f9f6f2", command=reset_game)
    restart_button.grid(row=5, column=3, padx=5, pady=5)
    # 更新界面
    update_ui()
    # 重设置排名
    label_ranking['text'] = '0'
    # 进入tkinter主事件循环
    root.mainloop()
