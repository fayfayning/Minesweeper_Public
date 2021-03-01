"""
Created on 5/6/20

@author: fayfayning
"""

'''
start with boxes
should i go back into minesweeper and edit it so that there are trackers for 
free, flags, bombs, and default? or maybe create lists with them?

presume flags are right

if box not 0?
for box ^
    if in range of box

separating checking equality line by line?

break into completely separate pieces and solve like that

for options
    for bombs in between the range
    how many ways to choose that many bombs from the total
    sum all of this up for each number of bombs
    from min to max sum of numbers of the free spaces

SPLIT SOLVER
local solver 1 by 1, 2 by 2, etc?
group all related boxes

random shape generator?
change bounds
update the hint function to reveal hints
double click to clear all
input board
    board save
    start from beginning (changes all to default)
    start from opening (acts according to status)
    
break down into small pieces, get those solutions
new equations for the big boi matrix
    
MAKE SURE THAT ALL OPTIONS ARE FOUND!!!!! NEED TO CHECK THE CONSTRAINTS FOR 
FREE SPACES FOR 
boxes = {(0, 0): [False, 1, 'default'], (0, 1): [False, 3, 'default'],
         (0, 2): [True, 2, 'flagged'], (0, 3): [False, 2, 'free'],
         (1, 0): [True, 1, 'default'], (1, 1): [False, 4, 'free'],
         (1, 2): [True, 3, 'flagged'], (1, 3): [False, 3, 'free'],
         (2, 0): [False, 1, 'default'], (2, 1): [False, 3, 'free'],
         (2, 2): [True, 2, 'bomb'], (2, 3): [False, 2, 'free']}

'''

import numpy as np
from itertools import product, combinations
import copy

def solve(boxes, bounds, d_bombs_left, d_free_spaces_left):

    print('boxes =', boxes)
    print('bounds =', bounds)
    print('d_bombs_left =', d_bombs_left)
    print('d_free_spaces_left =', d_free_spaces_left)

    free_spaces = [i for i in boxes.keys() if boxes[i][2] == 'free' and
                   boxes[i][1] != 0]
    count_dict = {}
    for i in free_spaces:
        count_dict[i] = [0, [], 0, [], 0, []]
        for j in range(bounds[i][0], bounds[i][1] + 1):
            for k in range(bounds[i][2], bounds[i][3] + 1):
                if (j, k) != i:
                    if boxes[(j, k)][2] == 'flagged' or boxes[(j, k)][2] == \
                            'bomb':
                        count_dict[i][0] += 1
                        count_dict[i][1].append((j, k))
                    elif boxes[(j, k)][2] == 'free':
                        count_dict[i][2] += 1
                        count_dict[i][3].append((j, k))
                    else:
                        count_dict[i][4] += 1
                        count_dict[i][5].append((j, k))

    equations = {}
    unsolved_spaces = [i for i in free_spaces if count_dict[i][4] != 0]
    for i in unsolved_spaces:
        equations[i] = [(boxes[i][1] - count_dict[i][0])]
        equations[i].append([j for j in count_dict[i][5]])
    print("equations", equations)
    relevant_list2 = []
    for i in unsolved_spaces:
        for j in equations[i][1]:
            relevant_list2.append(j)
    relevant_list2 = sorted(set(relevant_list2))
    print("relevant list", relevant_list2)

    equations_temp = {}
    equations_shortcut = {}
    for i in equations:
        equations_shortcut[i] = []
    for i in equations:
        equations_temp[i] = copy.deepcopy(equations[i][1])
    while True:
        count_temp = 0
        lst_temp = []
        for i in combinations(sorted(equations_temp.keys()), 2):
            if len(set(equations_temp[i[0]]) & set(equations_temp[i[1]])) != 0:
                equations_temp[i[0]] += [j for j in equations_temp[i[1]] if j
                                         not in equations_temp[i[0]]]
                equations_temp[i[1]] = equations_temp[i[0]]
                lst_temp.append(i[1])
                if tuple(i[1]) not in equations_shortcut[i[0]]:
                    equations_shortcut[i[0]].append(tuple(i[1]))
                for j in equations_shortcut[i[1]]:
                    if j not in equations_shortcut[i[0]]:
                        equations_shortcut[i[0]].append(j)
                equations_shortcut[i[1]] = equations_shortcut[i[0]]
                count_temp += 1
        for i in lst_temp:
            if i in equations_temp.keys():
                del equations_temp[i]
            if i in equations_shortcut.keys():
                del equations_shortcut[i]
        if count_temp == 0 or len(equations_temp.keys()) == 1:
            break
    print('equations temp', equations_temp)
    print('equations shortcut', equations_shortcut)
    works = {}
    name_dict = {}
    for i in equations_shortcut:
        mini_equations = {}
        for j in equations_shortcut[i]:
            mini_equations[j] = equations[j]
        mini_equations[i] = equations[i]
        print(mini_equations)
        a = np.zeros((len(mini_equations), (len(equations_temp[i]))), dtype =
        int)
        count2 = 0
        sorted_keys = sorted(mini_equations.keys())
        name_dict[i] = {}
        count = 0
        for j in equations_temp[i]:
            name_dict[i][j] = count
            count += 1
        for j in sorted_keys:
            for k in name_dict[i].keys():
                if k in mini_equations[j][1]:
                    a[count2][name_dict[i][k]] = 1
            count2 += 1
        results = np.array([[mini_equations[j][0] for j in sorted_keys]]).T
        print('results', results)
        print('array', a)
        works[i] = []

        options = [i for i in product([0, 1], repeat=len(equations_temp[i]))
                   if (sum(i) <= d_bombs_left)]
        for j in range(len((options))):
            options[j] = (np.array([options[j]])).T
            comparison = a @ options[j] == results
            if comparison.all():
                works[i].append(options[j])
        #print('works', works)

    work_lst = [works[i] for i in works]
    final_works = list(product(*work_lst))
    constraint_fail = []
    if final_works == [()]:
        print('hi')
        return [False, []]
    for i in range(len(final_works)):
        final_works[i] = np.vstack([j for j in final_works[i]])
        check1 = (np.sum(final_works[i]) <= d_bombs_left)
        check2 = (np.sum(final_works[i]) >= len(relevant_list2) -
              d_free_spaces_left)
        if not check1 or not check2:
            constraint_fail.append(i)
    constraint_count = 0
    for i in constraint_fail:
        del final_works[i + constraint_count]
        constraint_count -= 1
    print('final', final_works)
    ordered_lst = []
    for i in sorted(name_dict.keys()):
        for j in name_dict[i]:
            ordered_lst.append(j)
    print('ordered_lst', ordered_lst)

    solv_dict = {}
    for i in range(len(ordered_lst)):
        solv_dict[ordered_lst[i]] = []
        for j in final_works:
            solv_dict[ordered_lst[i]].append(j[i][0])
    solv_count_dict = {}
    for i in solv_dict:
        solv_count_dict[i] = len(set(solv_dict[i]))
    solv_list = [solv_count_dict[i] for i in sorted(solv_count_dict.keys())]
    if len(solv_list) == 0:
        return [False, []]
    elif min(solv_list) == 1:
        solved_boxes = sorted([[i, set(solv_dict[i])] for i in \
                solv_count_dict.keys() if solv_count_dict[i] == 1])
        print('solved boxes', solved_boxes)
        return [True, solved_boxes]
    return [False, []]

def test1():
    boxes = {(0, 0): [False, 1, 'default'], (0, 1): [False, 3, 'default'],
             (0, 2): [True, 2, 'flagged'], (0, 3): [False, 2, 'free'],
             (1, 0): [True, 1, 'default'], (1, 1): [False, 4, 'free'],
             (1, 2): [True, 3, 'flagged'], (1, 3): [False, 3, 'free'],
             (2, 0): [False, 1, 'default'], (2, 1): [False, 3, 'free'],
             (2, 2): [True, 2, 'bomb'], (2, 3): [False, 2, 'free']}
    bounds = {(0, 0): [0, 1, 0, 1], (0, 1): [0, 1, 0, 2], (0, 2): [0, 1, 1, 3],
              (0, 3): [0, 1, 2, 3], (1, 0): [0, 2, 0, 1], (1, 1): [0, 2, 0, 2],
              (1, 2): [0, 2, 1, 3], (1, 3): [0, 2, 2, 3], (2, 0): [1, 2, 0, 1],
              (2, 1): [1, 2, 0, 2], (2, 2): [1, 2, 1, 3], (2, 3): [1, 2, 2, 3]}
    d_bombs_left = 1
    d_free_spaces_left = 3
    return solve(boxes, bounds, d_bombs_left, d_free_spaces_left)


def test2():
    boxes = {(0, 0): [False, 3, 'free'], (0, 1): [True, 4, 'default'],
             (0, 2): [False, 3, 'default'], (0, 3): [False, 1, 'default'],
             (1, 0): [True, 4, 'default'], (1, 1): [True, 5, 'default'],
             (1, 2): [True, 3, 'default'], (1, 3): [False, 1, 'default'],
             (2, 0): [True, 3, 'default'], (2, 1): [False, 4, 'default'],
             (2, 2): [False, 2, 'default'], (2, 3): [False, 1, 'free']}
    bounds = {(0, 0): [0, 1, 0, 1], (0, 1): [0, 1, 0, 2], (0, 2): [0, 1, 1, 3],
              (0, 3): [0, 1, 2, 3], (1, 0): [0, 2, 0, 1], (1, 1): [0, 2, 0, 2],
              (1, 2): [0, 2, 1, 3], (1, 3): [0, 2, 2, 3], (2, 0): [1, 2, 0, 1],
              (2, 1): [1, 2, 0, 2], (2, 2): [1, 2, 1, 3], (2, 3): [1, 2, 2, 3]}
    d_bombs_left = 5
    d_free_spaces_left = 5
    return solve(boxes, bounds, d_bombs_left, d_free_spaces_left)

def test3():
    boxes = {(0, 0): [False, 2, 'free'], (0, 1): [True, 3, 'default'],
             (0, 2): [False, 3, 'default'], (0, 3): [False, 2, 'default'],
             (1, 0): [True, 2, 'default'], (1, 1): [False, 4, 'default'],
             (1, 2): [True, 4, 'default'], (1, 3): [True, 3, 'default'],
             (2, 0): [False, 1, 'default'], (2, 1): [False, 3, 'free'],
             (2, 2): [True, 3, 'default'], (2, 3): [False, 3, 'free']}
    bounds = {(0, 0): [0, 1, 0, 1], (0, 1): [0, 1, 0, 2], (0, 2): [0, 1, 1, 3],
              (0, 3): [0, 1, 2, 3], (1, 0): [0, 2, 0, 1], (1, 1): [0, 2, 0, 2],
              (1, 2): [0, 2, 1, 3], (1, 3): [0, 2, 2, 3], (2, 0): [1, 2, 0, 1],
              (2, 1): [1, 2, 0, 2], (2, 2): [1, 2, 1, 3], (2, 3): [1, 2, 2, 3]}
    d_bombs_left = 5
    d_free_spaces_left = 4
    return solve(boxes, bounds, d_bombs_left, d_free_spaces_left)

def test4():
    boxes = {(0, 0): [False, 0, 'free'], (0, 1): [False, 0, 'free'],
             (0, 2): [False, 0, 'free'], (0, 3): [False, 0, 'free'],
             (0, 4): [False, 0, 'free'], (0, 5): [False, 0, 'free'],
             (0, 6): [False, 1, 'free'], (0, 7): [True, 2, 'default'],
             (0, 8): [True, 2, 'default'], (1, 0): [False, 0, 'free'],
             (1, 1): [False, 0, 'free'], (1, 2): [False, 0, 'free'],
             (1, 3): [False, 0, 'free'], (1, 4): [False, 1, 'free'],
             (1, 5): [False, 1, 'free'], (1, 6): [False, 2, 'free'],
             (1, 7): [False, 2, 'default'], (1, 8): [False, 2, 'default'],
             (2, 0): [False, 0, 'free'], (2, 1): [False, 0, 'free'],
             (2, 2): [False, 0, 'free'], (2, 3): [False, 0, 'free'],
             (2, 4): [False, 1, 'free'], (2, 5): [True, 1, 'default'],
             (2, 6): [False, 1, 'default'], (2, 7): [False, 0, 'default'],
             (2, 8): [False, 0, 'default'], (3, 0): [False, 1, 'free'],
             (3, 1): [False, 1, 'free'], (3, 2): [False, 1, 'free'],
             (3, 3): [False, 0, 'free'], (3, 4): [False, 1, 'free'],
             (3, 5): [False, 1, 'default'], (3, 6): [False, 1, 'default'],
             (3, 7): [False, 0, 'default'], (3, 8): [False, 0, 'default'],
             (4, 0): [False, 1, 'default'], (4, 1): [True, 1, 'default'],
             (4, 2): [False, 1, 'free'], (4, 3): [False, 1, 'free'],
             (4, 4): [False, 1, 'free'], (4, 5): [False, 1, 'default'],
             (4, 6): [False, 0, 'default'], (4, 7): [False, 1, 'default'],
             (4, 8): [False, 1, 'default'], (5, 0): [False, 1, 'default'],
             (5, 1): [False, 1, 'default'], (5, 2): [False, 1, 'default'],
             (5, 3): [False, 1, 'default'], (5, 4): [True, 1, 'default'],
             (5, 5): [False, 1, 'default'], (5, 6): [False, 0, 'default'],
             (5, 7): [False, 1, 'default'], (5, 8): [True, 1, 'default'],
             (6, 0): [False, 1, 'default'], (6, 1): [False, 1, 'default'],
             (6, 2): [False, 0, 'default'], (6, 3): [False, 1, 'default'],
             (6, 4): [False, 1, 'default'], (6, 5): [False, 1, 'default'],
             (6, 6): [False, 0, 'default'], (6, 7): [False, 1, 'default'],
             (6, 8): [False, 1, 'default'], (7, 0): [True, 1, 'default'],
             (7, 1): [False, 2, 'default'], (7, 2): [False, 1, 'default'],
             (7, 3): [False, 2, 'default'], (7, 4): [False, 1, 'default'],
             (7, 5): [False, 1, 'default'], (7, 6): [False, 1, 'default'],
             (7, 7): [False, 1, 'default'], (7, 8): [False, 1, 'default'],
             (8, 0): [False, 1, 'default'], (8, 1): [False, 2, 'default'],
             (8, 2): [True, 1, 'default'], (8, 3): [False, 2, 'default'],
             (8, 4): [True, 1, 'default'], (8, 5): [False, 1, 'default'],
             (8, 6): [False, 1, 'default'], (8, 7): [True, 1, 'default'],
             (8, 8): [False, 1, 'free']}
    bounds = {(0, 0): [0, 1, 0, 1], (0, 1): [0, 1, 0, 2], (0, 2): [0, 1, 1, 3],
              (0, 3): [0, 1, 2, 4], (0, 4): [0, 1, 3, 5], (0, 5): [0, 1, 4, 6],
              (0, 6): [0, 1, 5, 7], (0, 7): [0, 1, 6, 8], (0, 8): [0, 1, 7, 8],
              (1, 0): [0, 2, 0, 1], (1, 1): [0, 2, 0, 2], (1, 2): [0, 2, 1, 3],
              (1, 3): [0, 2, 2, 4], (1, 4): [0, 2, 3, 5], (1, 5): [0, 2, 4, 6],
              (1, 6): [0, 2, 5, 7], (1, 7): [0, 2, 6, 8], (1, 8): [0, 2, 7, 8],
              (2, 0): [1, 3, 0, 1], (2, 1): [1, 3, 0, 2], (2, 2): [1, 3, 1, 3],
              (2, 3): [1, 3, 2, 4], (2, 4): [1, 3, 3, 5], (2, 5): [1, 3, 4, 6],
              (2, 6): [1, 3, 5, 7], (2, 7): [1, 3, 6, 8], (2, 8): [1, 3, 7, 8],
              (3, 0): [2, 4, 0, 1], (3, 1): [2, 4, 0, 2], (3, 2): [2, 4, 1, 3],
              (3, 3): [2, 4, 2, 4], (3, 4): [2, 4, 3, 5], (3, 5): [2, 4, 4, 6],
              (3, 6): [2, 4, 5, 7], (3, 7): [2, 4, 6, 8], (3, 8): [2, 4, 7, 8],
              (4, 0): [3, 5, 0, 1], (4, 1): [3, 5, 0, 2], (4, 2): [3, 5, 1, 3],
              (4, 3): [3, 5, 2, 4], (4, 4): [3, 5, 3, 5], (4, 5): [3, 5, 4, 6],
              (4, 6): [3, 5, 5, 7], (4, 7): [3, 5, 6, 8], (4, 8): [3, 5, 7, 8],
              (5, 0): [4, 6, 0, 1], (5, 1): [4, 6, 0, 2], (5, 2): [4, 6, 1, 3],
              (5, 3): [4, 6, 2, 4], (5, 4): [4, 6, 3, 5], (5, 5): [4, 6, 4, 6],
              (5, 6): [4, 6, 5, 7], (5, 7): [4, 6, 6, 8], (5, 8): [4, 6, 7, 8],
              (6, 0): [5, 7, 0, 1], (6, 1): [5, 7, 0, 2], (6, 2): [5, 7, 1, 3],
              (6, 3): [5, 7, 2, 4], (6, 4): [5, 7, 3, 5], (6, 5): [5, 7, 4, 6],
              (6, 6): [5, 7, 5, 7], (6, 7): [5, 7, 6, 8], (6, 8): [5, 7, 7, 8],
              (7, 0): [6, 8, 0, 1], (7, 1): [6, 8, 0, 2], (7, 2): [6, 8, 1, 3],
              (7, 3): [6, 8, 2, 4], (7, 4): [6, 8, 3, 5], (7, 5): [6, 8, 4, 6],
              (7, 6): [6, 8, 5, 7], (7, 7): [6, 8, 6, 8], (7, 8): [6, 8, 7, 8],
              (8, 0): [7, 8, 0, 1], (8, 1): [7, 8, 0, 2], (8, 2): [7, 8, 1, 3],
              (8, 3): [7, 8, 2, 4], (8, 4): [7, 8, 3, 5], (8, 5): [7, 8, 4, 6],
              (8, 6): [7, 8, 5, 7], (8, 7): [7, 8, 6, 8], (8, 8): [7, 8, 7, 8]}
    d_bombs_left = 10
    d_free_spaces_left = 43
    return solve(boxes, bounds, d_bombs_left, d_free_spaces_left)

def test5():
    boxes = {(0, 0): [False, 0, 'free'], (0, 1): [False, 0, 'free'],
             (0, 2): [False, 0, 'free'], (0, 3): [False, 0, 'free'],
             (0, 4): [False, 0, 'free'], (0, 5): [False, 1, 'free'],
             (0, 6): [False, 1, 'free'], (0, 7): [False, 1, 'free'],
             (0, 8): [False, 0, 'free'], (1, 0): [False, 1, 'free'],
             (1, 1): [False, 1, 'free'], (1, 2): [False, 1, 'free'],
             (1, 3): [False, 0, 'free'], (1, 4): [False, 1, 'free'],
             (1, 5): [False, 2, 'free'], (1, 6): [True, 2, 'bomb'],
             (1, 7): [False, 1, 'free'], (1, 8): [False, 0, 'free'],
             (2, 0): [False, 1, 'default'], (2, 1): [True, 1, 'default'],
             (2, 2): [False, 1, 'free'], (2, 3): [False, 0, 'free'],
             (2, 4): [False, 1, 'free'], (2, 5): [True, 2, 'flagged'],
             (2, 6): [False, 2, 'free'], (2, 7): [False, 1, 'free'],
             (2, 8): [False, 0, 'free'], (3, 0): [False, 2, 'default'],
             (3, 1): [False, 2, 'free'], (3, 2): [False, 1, 'free'],
             (3, 3): [False, 0, 'free'], (3, 4): [False, 1, 'free'],
             (3, 5): [False, 1, 'free'], (3, 6): [False, 2, 'free'],
             (3, 7): [False, 1, 'free'], (3, 8): [False, 1, 'free'],
             (4, 0): [True, 1, 'default'], (4, 1): [False, 1, 'free'],
             (4, 2): [False, 0, 'free'], (4, 3): [False, 0, 'free'],
             (4, 4): [False, 0, 'free'], (4, 5): [False, 0, 'free'],
             (4, 6): [False, 1, 'free'], (4, 7): [True, 2, 'default'],
             (4, 8): [False, 2, 'default'], (5, 0): [False, 1, 'default'],
             (5, 1): [False, 2, 'free'], (5, 2): [False, 1, 'free'],
             (5, 3): [False, 1, 'free'], (5, 4): [False, 0, 'free'],
             (5, 5): [False, 0, 'free'], (5, 6): [False, 1, 'free'],
             (5, 7): [False, 2, 'free'], (5, 8): [True, 2, 'default'],
             (6, 0): [False, 0, 'default'], (6, 1): [False, 1, 'default'],
             (6, 2): [True, 1, 'default'], (6, 3): [False, 1, 'free'],
             (6, 4): [False, 0, 'free'], (6, 5): [False, 0, 'free'],
             (6, 6): [False, 0, 'free'], (6, 7): [False, 1, 'free'],
             (6, 8): [False, 1, 'default'], (7, 0): [False, 1, 'default'],
             (7, 1): [False, 2, 'default'], (7, 2): [False, 2, 'free'],
             (7, 3): [False, 1, 'free'], (7, 4): [False, 0, 'free'],
             (7, 5): [False, 0, 'free'], (7, 6): [False, 1, 'free'],
             (7, 7): [False, 2, 'free'], (7, 8): [False, 2, 'default'],
             (8, 0): [False, 1, 'default'], (8, 1): [True, 1, 'default'],
             (8, 2): [False, 1, 'free'], (8, 3): [False, 0, 'free'],
             (8, 4): [False, 0, 'free'], (8, 5): [False, 0, 'free'],
             (8, 6): [False, 1, 'free'], (8, 7): [True, 2, 'default'],
             (8, 8): [True, 2, 'default']}
    bounds = {(0, 0): [0, 1, 0, 1], (0, 1): [0, 1, 0, 2], (0, 2): [0, 1, 1, 3],
              (0, 3): [0, 1, 2, 4], (0, 4): [0, 1, 3, 5], (0, 5): [0, 1, 4, 6],
              (0, 6): [0, 1, 5, 7], (0, 7): [0, 1, 6, 8], (0, 8): [0, 1, 7, 8],
              (1, 0): [0, 2, 0, 1], (1, 1): [0, 2, 0, 2], (1, 2): [0, 2, 1, 3],
              (1, 3): [0, 2, 2, 4], (1, 4): [0, 2, 3, 5], (1, 5): [0, 2, 4, 6],
              (1, 6): [0, 2, 5, 7], (1, 7): [0, 2, 6, 8], (1, 8): [0, 2, 7, 8],
              (2, 0): [1, 3, 0, 1], (2, 1): [1, 3, 0, 2], (2, 2): [1, 3, 1, 3],
              (2, 3): [1, 3, 2, 4], (2, 4): [1, 3, 3, 5], (2, 5): [1, 3, 4, 6],
              (2, 6): [1, 3, 5, 7], (2, 7): [1, 3, 6, 8], (2, 8): [1, 3, 7, 8],
              (3, 0): [2, 4, 0, 1], (3, 1): [2, 4, 0, 2], (3, 2): [2, 4, 1, 3],
              (3, 3): [2, 4, 2, 4], (3, 4): [2, 4, 3, 5], (3, 5): [2, 4, 4, 6],
              (3, 6): [2, 4, 5, 7], (3, 7): [2, 4, 6, 8], (3, 8): [2, 4, 7, 8],
              (4, 0): [3, 5, 0, 1], (4, 1): [3, 5, 0, 2], (4, 2): [3, 5, 1, 3],
              (4, 3): [3, 5, 2, 4], (4, 4): [3, 5, 3, 5], (4, 5): [3, 5, 4, 6],
              (4, 6): [3, 5, 5, 7], (4, 7): [3, 5, 6, 8], (4, 8): [3, 5, 7, 8],
              (5, 0): [4, 6, 0, 1], (5, 1): [4, 6, 0, 2], (5, 2): [4, 6, 1, 3],
              (5, 3): [4, 6, 2, 4], (5, 4): [4, 6, 3, 5], (5, 5): [4, 6, 4, 6],
              (5, 6): [4, 6, 5, 7], (5, 7): [4, 6, 6, 8], (5, 8): [4, 6, 7, 8],
              (6, 0): [5, 7, 0, 1], (6, 1): [5, 7, 0, 2], (6, 2): [5, 7, 1, 3],
              (6, 3): [5, 7, 2, 4], (6, 4): [5, 7, 3, 5], (6, 5): [5, 7, 4, 6],
              (6, 6): [5, 7, 5, 7], (6, 7): [5, 7, 6, 8], (6, 8): [5, 7, 7, 8],
              (7, 0): [6, 8, 0, 1], (7, 1): [6, 8, 0, 2], (7, 2): [6, 8, 1, 3],
              (7, 3): [6, 8, 2, 4], (7, 4): [6, 8, 3, 5], (7, 5): [6, 8, 4, 6],
              (7, 6): [6, 8, 5, 7], (7, 7): [6, 8, 6, 8], (7, 8): [6, 8, 7, 8],
              (8, 0): [7, 8, 0, 1], (8, 1): [7, 8, 0, 2], (8, 2): [7, 8, 1, 3],
              (8, 3): [7, 8, 2, 4], (8, 4): [7, 8, 3, 5], (8, 5): [7, 8, 4, 6],
              (8, 6): [7, 8, 5, 7], (8, 7): [7, 8, 6, 8], (8, 8): [7, 8, 7, 8]}
    d_bombs_left = 8
    d_free_spaces_left = 11
    return solve(boxes, bounds, d_bombs_left, d_free_spaces_left)

def test6():
    boxes = {(0, 0): [False, 2, 'free'], (0, 1): [False, 3, 'free'],
             (0, 2): [False, 2, 'free'], (0, 3): [False, 1, 'free'],
             (1, 0): [True, 3, 'flagged'], (1, 1): [True, 5, 'bomb'],
             (1, 2): [True, 4, 'flagged'], (1, 3): [False, 2, 'free'],
             (2, 0): [False, 3, 'default'], (2, 1): [True, 5, 'bomb'],
             (2, 2): [True, 4, 'bomb'], (2, 3): [False, 2, 'free']}
    bounds = {(0, 0): [0, 1, 0, 1], (0, 1): [0, 1, 0, 2], (0, 2): [0, 1, 1, 3],
              (0, 3): [0, 1, 2, 3], (1, 0): [0, 2, 0, 1], (1, 1): [0, 2, 0, 2],
              (1, 2): [0, 2, 1, 3], (1, 3): [0, 2, 2, 3], (2, 0): [1, 2, 0, 1],
              (2, 1): [1, 2, 0, 2], (2, 2): [1, 2, 1, 3], (2, 3): [1, 2, 2, 3]}
    d_bombs_left = 0
    d_free_spaces_left = 1
    return solve(boxes, bounds, d_bombs_left, d_free_spaces_left)

#test6()

if __name__ == '__main__':
    pass

'''
failed:
    min_lim = max(d_bombs_left - d_free_spaces_left, 0)
    max_lim = min(d_bombs_left, len(relevant_list2))
    options = []
    for i in range(min_lim, max_lim + 1):
        new = [i for i in combinations(range(len(relevant_list2)), i)]
        for j in new:
            new2 = [1 if k in j else 0 for k in range(len(relevant_list2))]
            options.append(new2)
            
            
equations_temp = {}
    equations_shortcut = {}
    for i in equations:
        equations_temp[i] = copy.deepcopy(equations[i][1])
    print('equations temp', equations_temp)
    while True:
        count_temp = 0
        lst_temp = []
        for i in combinations(sorted(equations_temp.keys()), 2):
            print('combo', i[0], i[1])
            if i[0] in equations_temp.keys():
                x = equations_temp[i[0]]
            else:
                x = equations_shortcut[i[0]]
            if i[1] in equations_temp.keys():
                y = equations_temp[i[0]]
            else:
                y = equations_shortcut[i[0]]
            print('set 1', x)
            print('set 2', y)
            if len(set(x) & set(y)) != 0:
                print('intersect')
                x += [j for j in y if j not in y]
                y = x
                #lst_temp.append(i[1])
                if i[1] in equations_temp.keys():
                    del equations_temp[i[1]]
                count_temp += 1
        print('lst_temp', lst_temp)
        #for i in lst_temp:
            #if i in equations_temp.keys():
                #del equations_temp[i]
        print('equations temp', equations_temp)
        if count_temp == 0 or len(equations_temp.keys()) == 1:
            break
    print(equations_temp)
    

min_lim = max(d_bombs_left - d_free_spaces_left, 0)
    max_lim = min(d_bombs_left, len(relevant_list2))
    options = []
    for i in range(min_lim, max_lim + 1):
        new = [i for i in combinations(range(len(relevant_list2)), i)]
        for j in new:
            new2 = [1 if k in j else 0 for k in range(len(relevant_list2))]
            options.append(new2)
'''