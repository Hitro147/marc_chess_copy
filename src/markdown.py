from collections import defaultdict
from urllib.parse import urlencode
import os
import re
import ast

import chess
import yaml

with open('data/settings.yaml', 'r') as settings_file:
    settings = yaml.load(settings_file, Loader=yaml.FullLoader)


def create_link(text, link):
    return f"[{text}]({link})"

def create_issue_link(source, dest_list):
    issue_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['move'], safe="{}"))

    ret = [create_link(dest, issue_link.format(source=source, dest=dest)) for dest in sorted(dest_list)]
    return ", ".join(ret)

    # issue_link_template = "https://github.com/Hitro147/marc_chess_copy/issues/create?repo={repo}&{params}"
    
    # # Hardcoding the repo and parameters
    # repo = "marc_chess_copy"
    # params_template = "move_source={source}&move_dest={dest}"
    
    # ret = [create_link(dest, issue_link_template.format(repo=repo, params=params_template.format(source=source, dest=dest))) for dest in sorted(dest_list)]
    # return ", ".join(ret)

def generate_top_moves():
    with open("data/top_moves.txt", 'r') as file:
        dictionary = ast.literal_eval(file.read())

    markdown = "\n"
    markdown += "| Total moves |  User  |\n"
    markdown += "| :---------: | :----- |\n"

    max_entries = settings['misc']['max_top_moves']
    for key,val in sorted(dictionary.items(), key=lambda x: x[1], reverse=True)[:max_entries]:
        if isinstance(key, str):
            markdown += "| {}   | {} |\n".format(val, create_link(key, "https://github.com/" + key[1:]))
        else:
            markdown += "| {}   | {} |\n".format(val, key)

    #print(markdown)
    return markdown + "\n"

def generate_last_moves():
    markdown = "\n"
    markdown += "| Move     | Author |\n"
    markdown += "| :--:     | :----- |\n"

    counter = 0

    with open("data/last_moves.txt", 'r') as file:
        for line in file.readlines():
            parts = line.rstrip().split(':')

            if not ":" in line:
                continue

            if counter >= settings['misc']['max_last_moves']:
                break

            counter += 1

            match_obj = re.search('([A-H][1-8])([A-H][1-8])', line, re.I)
            if match_obj is not None:
                source = match_obj.group(1).upper()
                dest   = match_obj.group(2).upper()

                markdown += "| `" + source + "` to `" + dest + "` | " + parts[1] + " |\n"
                
            else:
                markdown += "| `" + parts[0] + "` | " + parts[1] + " |\n"

    #print(markdown)
    return markdown + "\n"

def generate_moves_list(board):
    # Create dictionary and fill it
    moves_dict = defaultdict(set)

    for move in board.legal_moves:
        source = chess.SQUARE_NAMES[move.from_square].upper()
        dest   = chess.SQUARE_NAMES[move.to_square].upper()

        moves_dict[source].add(dest)

    # Write everything in Markdown format
    markdown = ""

    if board.is_game_over():
        issue_link = settings['issues']['link'].format(
            repo=os.environ["GITHUB_REPOSITORY"],
            params=urlencode(settings['issues']['new_game']))

        return "**GAME IS OVER!** " + create_link("Click here", issue_link) + " to start a new game :D\n"

    if board.is_check():
        markdown += "**CHECK!** Choose your move wisely!\n"

    markdown += "|  FROM  | TO |\n"
    markdown += "| :----: | :-------------- |\n"

    for source,dest in sorted(moves_dict.items()):
        markdown += "| **" + source + "** | " + create_issue_link(source, dest) + " |\n"
        #markdown += "| **" + source + "** | " + str(dest) + " |\n"

    #print(markdown)
    return markdown

def board_to_markdown(board):
    board_list = [[item for item in line.split(' ')] for line in str(board).split('\n')]
    markdown = ""

    # images = {
    #     "r": "Rook_B",
    #     "n": "Knight_B",
    #     "b": "Bishop_B",
    #     "q": "Queen_B",
    #     "k": "King_B",
    #     "p": "Pawn_B",

    #     "R": "Rook_W",
    #     "N": "Knight_W",
    #     "B": "Bishop_W",
    #     "Q": "Queen_W",
    #     "K": "King_W",
    #     "P": "Pawn_W",

    #     ".": "."
    # }

    images = {
        "r": "img/black/rook.png",
        "n": "img/black/knight.png",
        "b": "img/black/bishop.png",
        "q": "img/black/queen.png",
        "k": "img/black/king.png",
        "p": "img/black/pawn.png",

        "R": "img/white/rook.png",
        "N": "img/white/knight.png",
        "B": "img/white/bishop.png",
        "Q": "img/white/queen.png",
        "K": "img/white/king.png",
        "P": "img/white/pawn.png",

        ".": "img/blank.png"
    }

    # Write header in Markdown format
    markdown += "|   | A | B | C | D | E | F | G | H |   |\n"
    markdown += "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    #Check if it's Black's turn
    is_black_turn = not board.turn

    # Write board
    for row in range(1, 9):
        adjusted_row = 9 - row if not is_black_turn else row
        markdown += "| **" + str(adjusted_row) + "** | "
        #markdown += "| **" + str(9 - row) + "** | "
        # for elem in board_list[row - 1]:
        #     #markdown += "<img src=\"{}\" width=50px> | ".format(images.get(elem, "???"))
        #     markdown += "{} |".format(images.get(elem, "."))
        # markdown += "**" + str(9 - row) + "** |\n"

        for elem in board_list[8 - row] if is_black_turn else board_list[row - 1]:
            markdown += "<img src=\"{}\" width=50px> | ".format(images.get(elem, "???"))
            #markdown += "{} |".format(images.get(elem, "."))
        markdown += "**" + str(adjusted_row) + "** |\n"

    # Write footer in Markdown format
    markdown += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"

    print(markdown)
    return markdown
