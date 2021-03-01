"""
testing

Created on 5/3/20

@author: fayfayning

Version 7: Adding images for bombs and flags

"""

"""
Minesweeper Game

Features:
    Preset specifications based on skill level
    Will only accept valid integer game specifications
    You cannot hit a bomb on the first move
    Automatically clears out 0's
    Toggle flags on and off
    Flags and bombs have image displays
    Trackers for how many bombs/flags you have chosen, and how many free 
        spaces there are left
    Popups for victories and hitting bombs
    Can choose to continue if you hit a bomb
    Start new game at any time
    Click flag check to check if your flags are placed in the right locations
    Click hint to give you a hint
        Prompts solver module
        Tells you whether there are solved boxes
        If there are solved boxes, you can choose to open them (one at a 
        time, or all at once)
        Displays these requested solved boxes in list with a scrollbar
"""

import tkinter as tk
import random
from PIL import Image, ImageTk
import time
import Solver as slv

def game_screen(game_victory, game_board):
    '''
    Sets up starting screen, so that players can adjust their settings.
    Arguments: none
    Returns: frames/labels in the starting screen, game settings (length,
    width, bombs)
    External calls: none
    '''
    root.wm_resizable(False, False)
    game_screen_frame = tk.Frame(root)
    game_screen_frame.pack()
    game_screen_frame.grid_rowconfigure(6, minsize=50)
    title = tk.Label(game_screen_frame, text = 'Minesweeper', font = ("Comic "
                                                                 "Sans", 40))
    title.grid(column=0, columnspan=3, row=0, pady=10)

    custom_input = tk.Button(game_screen_frame, text='Import Custom Board',
                             font=('Comic Sans', 16), command = lambda:
        input_options(game_screen_frame, warning_frame, game_victory,
                      game_board))

    custom_input.grid(column=0, row=1, columnspan=3)

    game_specifications = tk.Label(game_screen_frame, text= 'Game '
                        'Specifications', font= ('Comic Sans', 18))
    game_specifications.grid(column=0, row=2)
    l_length = tk.Label(game_screen_frame, text = "Field length:")
    l_length.grid(column=0, row=3)
    length = tk.Entry(game_screen_frame, width = 20)
    length.grid(column=1, row=3)
    l_width = tk.Label(game_screen_frame, text = "Field width:")
    l_width.grid(column=0, row=4)
    width = tk.Entry(game_screen_frame, width = 20)
    width.grid(column=1, row=4)
    l_bombs = tk.Label(game_screen_frame, text = "Number of bombs:")
    l_bombs.grid(column=0, row=5)
    bombs = tk.Entry(game_screen_frame, width = 20)
    bombs.grid(column=1, row=5)
    game_screen_frame.grid_columnconfigure(2, minsize=250)
    spec_args = [length, width, bombs]
    presets = tk.Label(game_screen_frame, text='Preset Options', font = (
        'Comic Sans', 18))
    presets.grid(column=2, row=2)

    def preset_options(option):
        '''
        Adjusts settings to fit the selected preset option.
        '''
        preset_list = [(9, 9, 10), (16, 16, 40), (16, 30, 99)]
        length.delete(0, 'end')
        length.insert(0, preset_list[option][0])
        width.delete(0, 'end')
        width.insert(0, preset_list[option][1])
        bombs.delete(0, 'end')
        bombs.insert(0, preset_list[option][2])

    beginner = tk.Button(game_screen_frame, text='Beginner', command= lambda:
    preset_options(0))
    beginner.grid(column=2, row=3)
    intermediate = tk.Button(game_screen_frame, text='Intermediate', command= lambda:
    preset_options(1))
    intermediate.grid(column=2, row=4)
    expert = tk.Button(game_screen_frame, text='Expert', command= lambda:
    preset_options(2))
    expert.grid(column=2, row=5)
    warning_frame = tk.Frame(root, width =650, height = 70)
    warning_frame.pack()
    warning_frame.pack_propagate(False)
    author = tk.Label(warning_frame, text='Created by Fayfay Ning, Duke Class of'
        ' 2023', font = ('Comic Sans', 12, 'italic'))
    author.pack(side = 'bottom', pady=10)
    return [game_screen_frame, warning_frame, author, *spec_args]

def input_options(game_screen_frame, warning_frame, game_victory, game_board):
    height = root.winfo_height()
    width = root.winfo_width()
    root.minsize(width, height)
    game_screen_frame.forget()
    warning_frame.forget()
    instructions = tk.Label(root, text= 'Please input your board.',
                            font = ('Comic Sans', 16))
    instructions.pack(side='top', pady=(10, 10))
    entry_frame = tk.Frame(root)
    entry_frame.pack()
    scrollbar = tk.Scrollbar(entry_frame)
    scrollbar.pack(side='left')
    board_input = tk.Text(entry_frame, height = 10, highlightbackground =
        'black')
    board_input.pack(side='right')
    option_frame = tk.Frame(root)
    option_frame.pack()

    def clean_entry(board_input, setting):
        txt = board_input.get("1.0", "end-1c")
        lst = [(i + ']').strip() for i in txt.split('],')]
        dict = {}
        for i in lst:
            i = [j.strip() for j in i.split(':')]
            i[0] = ''.join(j for j in i[0] if j.isdigit() or j == ',')
            i[0] = i[0].split(',')
            i[0] = (int(i[0][0]), int(i[0][1]))
            i[1] = ''.join(
                j for j in i[1] if j.isalnum() or j in "'," or j == '"')
            i[1] = i[1].split(',')
            if i[1][0] == 'False':
                i[1][0] = False
            elif i[1][0] == 'True':
                i[1][0] = True
            i[1][1] = int(i[1][1])
            i[1][2] = (i[1][2].strip('"')).strip("'")
            dict[i[0]] = i[1]
        d_length = max([i[0] for i in dict]) + 1
        d_width = max([i[1] for i in dict]) + 1
        d_bombs = len([i for i in dict.values() if i[0]])
        clear_start_menu(game_screen_frame, warning_frame)

        game_board.set('True{}'.format(setting))

        entry_frame.forget()
        for widget in root.winfo_children():
            widget.forget()
        set_field(d_length, d_width, d_bombs, game_victory, game_board, dict)

    start_beginning = tk.Button(option_frame, text='Create Board '
        '(Start Anew)', command = lambda: (clean_entry(board_input, 0)))
    start_beginning.grid(column=0, row=0, padx = 10, pady= (15, 10))
    start_middle = tk.Button(option_frame, text='Create Board (Resume '
        'Progress)', command = lambda: clean_entry(board_input, 1))
    start_middle.grid(column=1, row=0, padx = 10, pady = (15, 10))
    random_generate = tk.Button(option_frame, text='Return to Random '
        'Generation', command = lambda: new_start())
    random_generate.grid(column=0, row=1, columnspan=2, padx=10, pady=(5, 10))
    guide = tk.Label(option_frame, text='Note: The proper format is a list, '
        'separated by commas, in the format (a, b): [c, d, e].\na is how many '
        'boxes down the given box is, minus 1, and b is how many '
        'boxes to\nthe right the given box is, minus 1. c is True for bombs '
        'and False for non-bombs. d is the\nnumber of bombs surrounding the '
        'given box. If you do not know d, you can put any random\nnumber '
        'there. e is the state of the box: "default" represents a covered '
        'box,\n "flagged" represents a flagged box, "bomb" represents an '
        'uncovered bomb, and "free"\nrepresents an uncovered non-bomb box. '
        'Below is an example of the format:\n(2, 2): [True, 2, "bomb"], (2, '
        '3): [False, 2, "free"]', font = ('Comic Sans', 12))
    guide.grid(column=0, row=2, columnspan=2, padx=10, pady=(5, 10))


    def new_start():
        quick_clear()
        game_board.set('False')
        r_game_screen = game_screen(game_victory, game_board)
        b_set_field = tk.Button(r_game_screen[0], text="Create Field",
            font=('Comic Sans', 16), command=lambda:
            field_parameters_and_run(*r_game_screen, game_victory, game_board))
        b_set_field.grid(column=0, row=6, columnspan=3, sticky='s')

    def quick_clear():
        for i in root.winfo_children():
            i.forget()

def field_parameters_and_run(game_screen_frame, warning_frame, author, length,
                             width, bombs, game_victory, game_board):
    '''
    Handles settings input from starting screen. Makes sure that the input is valid.
    Arguments: frames/labels in the starting screen, game settings (length,
    width, bombs), game victory
    Returns: none
    External calls:
        Itself: when input is not allowed
        clear_start_menu: if the input is allowed
        set_field: if the input is allowed
    '''
    field_parameters_and_run_args = [game_screen_frame, warning_frame, author,
        length, width, bombs, game_victory, game_board]
    try:
        d_length = int(length.get())
        d_width = int(width.get())
        d_bombs = int(bombs.get())
        if d_length < 1 or d_width < 1 or d_bombs < 1 or d_length * d_width \
                <= d_bombs:
            b_set_field = tk.Button(game_screen_frame, text="Create Field",
                font = ('Comic Sans', 16), command= lambda:
                field_parameters_and_run(*field_parameters_and_run_args))
            b_set_field.grid(column=0, row=6, columnspan=3, sticky='s')
            warning = tk.Label(warning_frame, text="Please input valid "
                "specifications. Number of bombs cannot equal or exceed total "
                "number of spaces.")
            for widget in warning_frame.winfo_children():
                if widget != author:
                    widget.pack_forget()
            warning.pack()
        else:
            dict = {}
            clear_start_menu(game_screen_frame, warning_frame)
            set_field(d_length, d_width, d_bombs, game_victory, game_board,
                dict)
    except ValueError:
        b_set_field = tk.Button(game_screen_frame, text="Create Field",
                                font = ('Comic Sans', 16),
                    command= lambda: field_parameters_and_run(
                        *field_parameters_and_run_args))
        b_set_field.grid(column=0, row=6, columnspan=3, sticky='s')
        non_integers = tk.Label(warning_frame, text="Please input valid "
            "specifications. Only integers are allowed.")
        for widget in warning_frame.winfo_children():
            if widget != author:
                widget.pack_forget()
        non_integers.pack()

def clear_start_menu(game_screen_frame, warning_frame):
    '''
    Clears the starting screen
    Arguments: frames in the starting screen
    Returns: none
    External calls: none
    '''
    game_screen_frame.pack_forget()
    warning_frame.pack_forget()

def set_field_back(box, d_bombs, boxes, bounds):
    boxes_without_first = [i for i in boxes.keys() if i != box]
    bomb_boxes = random.sample(boxes_without_first, d_bombs)
    for i in bomb_boxes:
        boxes[i][0] = True
        for a in range(bounds[i][0], bounds[i][1]+1):
            for b in range(bounds[i][2], bounds[i][3]+1):
                boxes[(a, b)][1] += 1
    print('boxes', boxes)

def set_field(d_length, d_width, d_bombs, game_victory, game_board, dict):
    root.minsize(0, 0)
    f_top = tk.Frame(root)
    f_top.pack()
    f_middle = tk.Frame(root)
    f_middle.pack()
    f_bottom = tk.Frame(root)
    f_bottom.pack()
    for col in range(d_width):
        f_bottom.grid_columnconfigure(col, minsize=50)
    for row in range(d_length):
        f_bottom.grid_rowconfigure(row, minsize=25)
    heading1 = tk.Label(f_top, text = "Size: " + str(d_length) + " x " + str(
        d_width) + "    ")
    heading1.grid(column=0, row=0)
    heading2 = tk.Label(f_top, text = "Total Bombs: " + str(d_bombs) + "    ")
    heading2.grid(column=1, row=0)
    d_bombs_left = tk.IntVar()
    d_bombs_left.set(d_bombs)
    d_bombs_left_str = tk.StringVar()
    d_bombs_left_str.set("Number of Bombs Left: {}    ".format(
        d_bombs_left.get()))
    heading3 = tk.Label(f_top, textvariable = d_bombs_left_str)
    heading3.grid(column=0, row=1)
    d_free_spaces_left = tk.IntVar()
    d_free_spaces_left.set((d_length * d_width) - d_bombs)
    d_free_spaces_left_str = tk.StringVar()
    d_free_spaces_left_str.set("Number of Free Spaces Left: {}    ".format(
        d_free_spaces_left.get()))
    heading4 = tk.Label(f_top, textvariable=d_free_spaces_left_str)
    heading4.grid(column=1, row=1)
    heading5 = tk.Button(f_middle, text="New Game", command=lambda:
    (clear_game(f_top, f_middle, f_bottom), run_game()))
    heading5.grid(column=0, row=0, columnspan=2)
    variable1 = 0
    heading6 = tk.Button(f_middle, text="Flag Check", command=lambda:
    flag_check_display(variable1, boxes, click_count, game_victory))
    heading6.grid(column=0, row=1, padx=60, pady=(0, 5))
    boxes = {}
    bounds = {}
    for i in range(d_length):
        for j in range(d_width):
            boxes[(i, j)] = [False, 0, 'default']
            bounds[(i, j)] = [max(0, i - 1), min(d_length - 1, i + 1),
                         max(0, j - 1), min(d_width - 1, j + 1)]
    if game_board.get()[:4] == 'True':
        boxes.clear()
        for i in dict:
            boxes[i] = [dict[i][0], 0, dict[i][2] if game_board.get()[-1] ==
                                                     '1' else 'default']
        for i in dict:
            if dict[i][0]:
                for a in range(bounds[i][0], bounds[i][1] + 1):
                    for b in range(bounds[i][2], bounds[i][3] + 1):
                        boxes[(a, b)][1] += 1

    click_count = tk.IntVar()
    click_count.set(0)
    boxes_buttons = {}
    click_args = [d_bombs, boxes, bounds, f_top, f_middle, f_bottom,
                         d_bombs_left, d_bombs_left_str, d_free_spaces_left,
                         d_free_spaces_left_str, boxes_buttons, click_count,
                         game_victory, game_board]

    for i in boxes.keys():
        boxes_buttons[i] = tk.Button(f_bottom, command = lambda box=i: click(
            box, *click_args))
        boxes_buttons[i].bind("<Button-2>", lambda event, box=i: right_click(
            event, box, *click_args))
        boxes_buttons[i].grid(column=i[1], row=i[0], sticky="wens")

    def hint_process(box_statuses, *click_args):
        try:
            for i in box_statuses:
                boxes_buttons[i[0]].configure(highlightbackground = 'red')
                boxes_buttons[i[0]].update()
            if len(box_statuses) != 0:
                time.sleep(1)
            for i in box_statuses:
                if list(i[1])[0] == 1:
                    event = None
                    right_click(event, i[0], *click_args)
                else:
                    click(i[0], *click_args)
        except TypeError:
            pass

    heading7 = tk.Button(f_middle, text="Hint", command=lambda:
        hint_process(hint(boxes, game_victory, click_count,
        d_bombs, d_bombs_left, d_free_spaces_left, bounds), *click_args))
    heading7.grid(column=1, row=1, padx=80, pady=(0, 5))

    if game_board.get() == 'True1':
        for i in boxes:
            if boxes[i][2] == 'flagged' or boxes[i][2] == 'bomb':
                boxes[i][2] = 'default'
                event = None
                right_click(event, i, *click_args)
            elif boxes[i][2] == 'free':
                boxes[i][2] = 'default'
                click(i, *click_args)
    print('boxes', boxes)

def flag_check(boxes):
    flag_check_int = 0
    for i in boxes:
        if boxes[i][2] == 'flagged':
            if boxes[i][0] == False:
                flag_check_int += 1
    return flag_check_int

def flag_check_display(variable1, boxes, click_count, game_victory):
    if click_count.get() > 0 and game_victory.get() == 'False':
        flag_check_int = flag_check(boxes)
        flag_check_str = "You have " + str(flag_check_int) + " Wrong Flag(s)."
        flag_check_popup = tk.Toplevel(root)
        flag_check_popup.withdraw()
        flag_check_popup.title('Flag Check')
        flag_check_popup.grab_set()
        flag_check_popup.attributes('-topmost', True)
        flag_check_popup.wm_resizable(False, False)
        message = tk.Label(flag_check_popup, text=flag_check_str)
        message.grid(column=0, row=0, padx=10, pady=(10))
        exit = tk.Button(flag_check_popup, text="Continue",
                             command= lambda: (
                                 flag_check_popup.grab_release(),
                                     flag_check_popup.destroy()))
        exit.grid(column=0, row=1, padx=10, pady=(0, 10))
        center_toplevel(flag_check_popup, root)
        flag_check_popup.deiconify()
        flag_check_popup.wm_protocol(name='WM_DELETE_WINDOW', func= lambda:
            (flag_check_popup.grab_set(), flag_check_popup.grab_release(),
            flag_check_popup.destroy()))

def hint(boxes, game_victory, click_count, d_bombs, d_bombs_left,
         d_free_spaces_left, bounds):

    requested_boxes = []
    if click_count.get() > 0 and game_victory.get() == 'False':
        hint_popup = tk.Toplevel(root)
        hint_popup.withdraw()
        hint_popup.title('Hint')
        hint_popup.grab_set()
        hint_popup.attributes('-topmost', True)
        h_top = tk.Frame(hint_popup)
        h_top.pack(fill='both', expand=True)
        h_top.rowconfigure(0, weight=1)
        h_top.columnconfigure(0, weight=1)
        h_bottom = tk.Frame(hint_popup)
        h_bottom.pack(fill='both', expand=True)
        hint_popup.wm_protocol(name='WM_DELETE_WINDOW', func=lambda:
        (hint_popup.grab_set(), hint_popup.grab_release(),
            hint_popup.destroy()))
        flag_check_int = flag_check(boxes)
        if flag_check_int != 0:
            flag_check_str1 = "You have " + str(flag_check_int) + " Wrong " \
                                                                  "Flag(s)"
            message1 = tk.Label(h_top, text=flag_check_str1)
            message1.grid(column=0, row=0, padx=10, pady=10)
            exit1 = tk.Button(h_bottom, text="Continue",
                              command=lambda: (
                                  hint_popup.grab_release(),
                                  hint_popup.destroy()))
            exit1.grid(column=0, row=0, padx=10, pady=(0, 10))
            h_bottom.grid_rowconfigure(0, weight=1)
            h_bottom.grid_columnconfigure(0, weight=1)
            hint_popup.wm_resizable(False, False)
            requested_boxes = None
        else:
            flag_check_str2 = "All of your flags are correct."
            message2 = tk.Label(h_top, text=flag_check_str2)
            message2.grid(column=0, row=0, padx=10, pady=(10, 0))
            hint_result = slv.solve(boxes, bounds,
                                       d_bombs_left.get(),
                                       d_free_spaces_left.get())
            label_place = 0
            solvable_str = tk.StringVar()
            if hint_result[0]:
                solvable_str.set("This is solvable. There are {} solved " \
                               "boxes.".format(len(hint_result[1])))
                hint_result_random = random.sample(hint_result[1],
                                                   len(hint_result[1]))
                random_box_count = tk.IntVar()
                random_box_count.set(0)
                repeat_check = tk.BooleanVar()
                repeat_check.set(False)
                scrollbar = tk.Scrollbar(h_top)
                listbox = tk.Listbox(h_top, yscrollcommand=scrollbar.set,
                                     height=1)
                scrollbar.config(command=listbox.yview)

                def solve_box(listbox, scrollbar, bool):
                    if random_box_count.get() == 0 and not repeat_check.get():
                        message2.grid_forget()
                        listbox.pack(side='left', fill="both", expand=True)
                        scrollbar.pack(side='right', fill="y")
                    height_popup = hint_popup.winfo_height()
                    width_popup = hint_popup.winfo_width()
                    hint_popup.minsize(width=width_popup, height=height_popup)
                    box = hint_result_random[random_box_count.get()]
                    if box not in requested_boxes:
                        requested_boxes.append(box)
                    if list(box[1])[0] == 0:
                        status = "not a bomb"
                    else:
                        status = "a bomb"
                    new_box = "Box at row {}, column {} is {}.".format(box[0][0]
                        + 1, box[0][1] + 1, status)
                    if not repeat_check.get():
                        listbox.insert(random_box_count.get(), new_box)
                    solvable_str.set("Game will update upon return.")
                    if random_box_count.get() + 1 == len(hint_result_random):
                        random_box_count.set(0)
                        repeat_check.set(True)
                    else:
                        random_box_count.set(random_box_count.get() + 1)
                        if bool:
                            solve_box(listbox, scrollbar, bool)

                sample_box = tk.Button(h_bottom, text="Solve a Random Box",
                                       command=lambda: solve_box(listbox,
                                           scrollbar, False))
                sample_box.grid(column=0, row=1, padx=10, pady=(10, 0))
                solve_all = tk.Button(h_bottom, text="Solve All Boxes",
                                    command=lambda: solve_box(listbox,
                                                              scrollbar, True))
                solve_all.grid(column=1, row=1, padx=10, pady=(10, 0))
                label_place += 1
            else:
                hint_result_random = []
                random_box_count = tk.IntVar()
                random_box_count.set(0)
                solvable_str.set("This is unsolvable.")
            message3 = tk.Label(h_bottom, textvariable=solvable_str)
            message3.grid(column=0, row=0, columnspan=2, padx=10, pady=(10, 0))
            exit2 = tk.Button(h_bottom, text="Return to Screen",
                              command=lambda: (
                                  hint_popup.grab_release(),
                                  hint_popup.destroy()))
            exit2.grid(column=0, row=1 + label_place, columnspan = 2, padx=10,
                       pady=10)
        for row in range(h_bottom.grid_size()[1]):
            h_bottom.grid_rowconfigure(row, weight=1)
        for col in range(h_bottom.grid_size()[0]):
            h_bottom.grid_columnconfigure(col, weight=1)
        center_toplevel(hint_popup, root)
        hint_popup.deiconify()
        hint_popup.wm_resizable(False, False)
        root.wait_window(hint_popup)
        return requested_boxes

def click(box, d_bombs, boxes, bounds, f_top, f_middle, f_bottom,
          d_bombs_left, d_bombs_left_str, d_free_spaces_left,
          d_free_spaces_left_str, boxes_buttons, click_count, game_victory,
          game_board):
    click_inner_args = [d_bombs, boxes, bounds, f_top, f_middle, f_bottom,
          d_bombs_left, d_bombs_left_str, d_free_spaces_left,
          d_free_spaces_left_str, boxes_buttons, click_count, game_victory,
            game_board]
    if click_count.get() == 0 and game_board.get()[:4] != 'True':
        set_field_back(box, d_bombs, boxes, bounds)
    click_count.set(click_count.get() + 1)
    if boxes[box][2] == 'default' and not boxes[box][0] and \
        d_free_spaces_left.get() == 1 and game_victory.get() == 'False':
        victory(f_top, f_middle, f_bottom)
        game_victory.set('True')
        for box2 in boxes.keys():
            if boxes[box2][2] == 'default' and box2 != box:
                event = 0
                right_click(event, box2, *click_inner_args)
    if boxes[box][2] == 'default':
        boxes_buttons[box].grid_forget()
        if boxes[box][0]:
            tk.load = Image.open("Bomb.jpg").resize((20, 20),
                                                    Image.ANTIALIAS)
            tk.render = ImageTk.PhotoImage(tk.load)
            boxes_buttons[box] = tk.Label(f_bottom, image=tk.render,
                                          height=1, width=1)
            boxes_buttons[box].image = tk.render
            boxes_buttons[box].grid(column = box[1], row = box[0],
                                    sticky="wens")
            boxes[box][2] = 'bomb'
            hit_bomb(d_bombs_left, d_bombs_left_str, game_victory, f_top,
                f_middle, f_bottom)
        else:
            boxes_buttons[box] = tk.Label(f_bottom, text = str(boxes[box][
                                                                   1]),
                                          font = ('Comic Sans', 12))
            boxes_buttons[box].grid(column = box[1], row = box[0],
                                    sticky="wens")
            d_free_spaces_left.set(d_free_spaces_left.get() - 1)
            d_free_spaces_left_str.set(
                "Number of Free Spaces Left: {}    ".format(
                    d_free_spaces_left.get()))
            boxes[box][2] = 'free'
            if boxes[box][1] == 0:
                for a in range(bounds[box][0], bounds[box][1] + 1):
                    for b in range(bounds[box][2], bounds[box][3] + 1):
                        click((a, b), *click_inner_args)

def victory(f_top, f_middle, f_bottom):
    victory_popup = tk.Toplevel(root)
    victory_popup.grab_set()
    victory_popup.attributes('-topmost', True)
    victory_popup.title('You Won!')
    message = tk.Label(victory_popup, text='Congratulations! You Won!',
                       font=('Comic Sans', 20))
    message.grid(column=0, row=0, columnspan=2, padx=10, pady=(10, 0))
    next_game = tk.Button(victory_popup, text="Next Game", command=lambda:
    (victory_popup.grab_release(), victory_popup.destroy(), clear_game(f_top,
        f_middle, f_bottom), run_game()))
    next_game.grid(column=1, row=1, padx=10, pady=10)
    stay_on_screen = tk.Button(victory_popup, text="Return to Screen", command=
    lambda: (victory_popup.grab_release(), victory_popup.destroy()))
    stay_on_screen.grid(column=0, row=1, padx=10, pady=10)
    center_toplevel(victory_popup, root)
    victory_popup.deiconify()
    victory_popup.wm_protocol(name='WM_DELETE_WINDOW', func= lambda:
        (victory_popup.grab_set(), victory_popup.grab_release(),
         victory_popup.destroy()))

def right_click(event, box, d_bombs, boxes, bounds, f_top, f_middle, f_bottom,
     d_bombs_left, d_bombs_left_str, d_free_spaces_left,
     d_free_spaces_left_str, boxes_buttons, click_count, game_victory,
    game_board):
    click_args_rc_inner = [d_bombs, boxes, bounds, f_top, f_middle, f_bottom,
            d_bombs_left, d_bombs_left_str, d_free_spaces_left,
            d_free_spaces_left_str, boxes_buttons, click_count, game_victory,
            game_board]

    if boxes[box][2] == 'default':
        boxes_buttons[box].grid_forget()
        tk.load2 = Image.open('Flag.png').resize((13, 15), Image.ANTIALIAS)
        tk.render2 = ImageTk.PhotoImage(tk.load2)
        boxes_buttons[box] = tk.Label(f_bottom, image=tk.render2,
                                      height=1, width=1)
        boxes_buttons[box].image = tk.render2
        boxes_buttons[box].bind("<Button-2>", lambda event:
            right_click(event, box, *click_args_rc_inner))
        boxes_buttons[box].grid(column = box[1], row = box[0], sticky="wens")
        boxes[box][2] = 'flagged'
        d_bombs_left.set(d_bombs_left.get() - 1)
        d_bombs_left_str.set("Number of Bombs Left: {}    ".format(
            d_bombs_left.get()))
    elif boxes[box][2] == 'flagged':
        boxes_buttons[box].grid_forget()
        boxes_buttons[box] = tk.Button(f_bottom, height=1, width=5,
            command=lambda: click(box, *click_args_rc_inner))
        boxes_buttons[box].bind("<Button-2>", lambda event:
        right_click(event, box, *click_args_rc_inner))
        boxes_buttons[box].grid(column=box[1], row=box[0], sticky="wens")
        boxes[box][2] = 'default'
        d_bombs_left.set(d_bombs_left.get() +1)
        d_bombs_left_str.set("Number of Bombs Left: {}    ".format(
            d_bombs_left.get()))

def hit_bomb(d_bombs_left, d_bombs_left_str, game_victory, f_top, f_middle,
             f_bottom):
    d_bombs_left_str
    d_bombs_left.set(d_bombs_left.get() - 1)
    d_bombs_left_str.set("Number of Bombs Left: {}    ".format(
        d_bombs_left.get()))
    if game_victory.get() == 'False':
        bomb_popup = tk.Toplevel(root)
        bomb_popup.grab_set()
        bomb_popup.attributes('-topmost', True)
        bomb_popup.title('You Hit a Bomb!')
        bomb_popup.wm_protocol(name='WM_DELETE_WINDOW',
                               func= lambda: (bomb_popup.grab_set(),
                    bomb_popup.grab_release(), bomb_popup.destroy()))
        message = tk.Label(bomb_popup, text = 'You Hit a Bomb!', font = ('Comic '
            'Sans', 20))
        message.grid(column=0, row=0, columnspan=2, padx=10, pady=(10,0))
        continue_playing = tk.Button(bomb_popup, text = "Continue", command =
            lambda: (bomb_popup.grab_release(), bomb_popup.destroy()))
        continue_playing.grid(column=0, row=1, padx=10, pady=10)
        accept_loss = tk.Button(bomb_popup, text = "End Game", command = lambda:
            (bomb_popup.grab_release(), bomb_popup.destroy(), clear_game(f_top,
                        f_middle, f_bottom), run_game()))
        accept_loss.grid(column=1, row=1, padx=10, pady=10)
        center_toplevel(bomb_popup, root)
        bomb_popup.deiconify()

def clear_game(f_top, f_middle, f_bottom):
    f_top.pack_forget()
    f_middle.pack_forget()
    f_bottom.pack_forget()

def center_toplevel(toplevel, root):
    root.update_idletasks()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    toplevel.deiconify()
    toplevel_width = toplevel.winfo_width()
    toplevel_height = toplevel.winfo_height()
    toplevel.withdraw()
    new_x = root_x + root_width / 2 - toplevel_width / 2
    new_y = root_y + root_height / 2 - toplevel_height / 2
    toplevel.geometry('+{}+{}'.format(int(new_x), int(new_y)))

def run_game():
    game_victory = tk.StringVar()
    game_victory.set('False')
    game_board = tk.StringVar()
    game_board.set('False')
    r_game_screen = game_screen(game_victory, game_board)
    b_set_field = tk.Button(r_game_screen[0], text="Create Field",
        font = ('Comic Sans', 16), command=lambda:
        field_parameters_and_run(*r_game_screen, game_victory, game_board))
    b_set_field.grid(column=0, row=6, columnspan=3, sticky='s')

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('+0+0')
    root.title('Minesweeper Game')

    run_game()

    root.mainloop()


'''
To do:

Do this stuff but with classes instead

Create separators
    ttk.separators
    create labels with lines underneath everything
Add some distance on the sides of the game board so its not too tight
/Add number limits to the input of length, width, number of bombs
/Change so button/label size stays uniform
/If 0 everything clears
/Beginner, intermediate, expert, etc. modes
Space out popups so that it always appears in the center of the screen
/Add buttons for exit (on screen, when you hit a bomb, when you win)
/Replace bomb and flag with images
/Flag check
Bombs hit tracker
Standardize fonts/sizes
Option to see revealed board
    Open during game
    Or when you win/lose
/Remove global variables
/Can't do flag check when you already won
/Set size at start, but change size when the field is set
Popups have to stay directly on top of window, can't get separated
Square blocks
Instead of 0, the block is blank
Best guess option (you have to guess, or maybe it'll autofix it)
Change bounds so they're a list of boxes around it

Ideas:
Array
__init__
args, kwargs
Exec
Self
Weight
Sticky
Validate
When do you need to carry over all the arguments?

Expansion:
Double click
    if the box is solved, it'll clear everything
    If it isn't you'll hit a bomb?
Timer - says you won when you win
Death tracker
Adjust size of screen to size of field
Add an undo button
When there are no guessable choices, ask if you would like a hint and carry 
out that hint
Different game modes - normal games, infinite lives, x many lives
/Bomb won't spawn where you first click
    Either spawn after first click
    Or, after spawn, relocate bomb to somewhere random -> make all the bomb 
    info tkinter variables then
Separate users and track their progress
    Login to separate users
    Require password for that user
    Track states in a data sheet for that user
    Option to delete/change games, or clear history for that user
If you try to flag check before the stage has been set, you get a popup message
Toggle features: clearing out 0's, dying on the first click
/Automatically flags bombs when you win

Questions:
Why do you need an extra argument for lambda?
'''